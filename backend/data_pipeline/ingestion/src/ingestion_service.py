from typing import Optional
from praw import Reddit
from praw.models import Comment
from praw.models import Submission
from psycopg_pool.pool import ConnectionPool
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from src.api.job_state import JobState
from src.api.schemas import IngestionResult
from src.api.schemas import ProcessedRedditComment
from src.core.logger import StructuredLogger
from src.product_detector.base import ProductDetector
from src.product_normalizer.base import ProductNormalizer
from src.utils.fetch_comments import fetch_comments
from src.utils.fetch_post import fetch_post_delayed
from src.db_utils.queries import batch_insert_raw_comments
from src.preprocessing.demojify import demojify
from src.preprocessing.url_remover import remove_url
from src.preprocessing.check_english import detect_english
from src.preprocessing.is_valid_comment import is_valid_comment
from src.preprocessing.relevant_fields import extract_relevant_fields
import prawcore


class IngestionService:
    def __init__(
        self,
        reddit_client: Reddit,
        db_pool: ConnectionPool,
        logger: StructuredLogger,
        topic_list: list[str],
        subreddit_list: list[str],
        normalizer: ProductNormalizer,
        detectors: dict[str, Optional[ProductDetector]],
        fetch_executor: ThreadPoolExecutor,
    ) -> None:
        self.reddit_client = reddit_client
        self.db_pool = db_pool
        self.logger = logger
        self._topic_list = topic_list
        self.subreddit_list = subreddit_list
        self._normalizer = normalizer
        self._detectors = detectors
        self.fetch_executor = fetch_executor
        self._batch_size = 100

        # cancellation flag, used to request graceful shutdown
        self.cancel_requested = False

    def run_single_cycle(self, job_state: JobState) -> None:
        """
        Run one complete ingestion cycle and update job state
        runs in a background thread and handles all errors internally and updates the job state

        Args:
            job_state: JobState instance to update with progress/results

        Raise:
            Value error if not job state
        """
        # nested import to prevent circular dependency import errors
        from src.api.signal_handler import run_state

        if not job_state:
            raise ValueError("Job state must be provided for the run single cycle")

        try:
            result = self._run_ingestion_pipeline()

            job_state.complete_job(result)

            self.logger.info(
                event_type="ingestion_service run",
                message=f"Ingestion completed: {result.posts_processed} posts, {result.comments_inserted} comments processed",
            )

        except Exception as e:
            self.logger.error(
                event_type="ingestion_service run", message=f"Ingestion failed: {str(e)}"
            )
            job_state.fail_job(str(e))
        finally:
            # Clean up run state after job completes or fails
            run_state.run_in_progress = False
            run_state.current_service = None

    @staticmethod
    def _preprocess_comment_text(text: str) -> tuple[str, bool]:
        """
        Preprocess comment text through cleaning pipeline
        Remove URL -> convert emojis -> detect language
        """
        url_removed = remove_url(text)
        demojified = demojify(url_removed)
        is_english = detect_english(demojified) == "en"

        return demojified, is_english

    def _fetch_all_posts(self) -> list[Submission]:
        """
        Fetch posts from all subreddits with per-subreddit error handling

        Returns:
           all_posts: list containing reddit post submission objects
        """
        all_posts = []

        futures = {
            self.fetch_executor.submit(
                fetch_post_delayed, self.reddit_client, subreddit, self.logger
            ): subreddit
            for subreddit in self.subreddit_list
        }

        for future in as_completed(futures):
            subreddit = futures[future]
            try:
                posts = future.result()
                if posts:
                    all_posts.extend(posts)
            except prawcore.exceptions.ServerError as e:
                self.logger.error(
                    event_type="Subreddit Fetch",
                    message=f"Reddit API server error for r/{subreddit}: {e}",
                )
            except Exception as e:
                self.logger.error(
                    event_type="Subreddit Fetch",
                    message=f"Failed to fetch from r/{subreddit}: {e}",
                )

        return all_posts

    def _process_comment(
        self, comment: Comment, detector: Optional[ProductDetector], topic: str
    ) -> ProcessedRedditComment | None:
        """
        Extract, transform, and filter a comment

        Args:
            comment: single Praw reddit comment object
            detector: pre-built product detector for the topic
            topic: the product topic we are trying to process for

        Returns:
            ProcessedRedditComment: Pydantic data object with relevant fields from the
                        comment like post_id, text, author, timestamp, upvotes
            None: none is returned if the comment is invalid
        """
        # Skip if no detector for this topic
        if (
            not detector
            or not is_valid_comment(comment)
            or not detector.contains_product(comment.body)
        ):
            return None

        products_in_comment: list[str] = detector.extract_products(comment.body)
        normalized_product_name: list[str] = self._normalizer.normalize_product_list(
            topic, products_in_comment
        )

        # extracting only relevant parts of the comment api res
        extracted: ProcessedRedditComment = extract_relevant_fields(
            comment, normalized_product_name
        )
        preprocessed_text, is_english = self._preprocess_comment_text(extracted.comment_body)
        if not is_english:
            return None

        return ProcessedRedditComment(
            comment_id=extracted.comment_id,
            comment_body=preprocessed_text,
            subreddit=extracted.subreddit,
            detected_products=extracted.detected_products,
            timestamp=extracted.timestamp,
            score=extracted.score,
            author=extracted.author,
            post_id=extracted.post_id,
            topic=topic,
        )

    def _batch_insert_to_db(self, comment_list: list[ProcessedRedditComment]) -> None:
        """
        Method for taking in a batch of valid comments, converting it into a dict,
        and batch writing to PG table

        Args:
            comment_list: list of reddit comment
        """
        # Convert to dict format expected by batch_insert
        comment_dicts = [
            {
                "comment_id": comment.comment_id,
                "post_id": comment.post_id,
                "comment_body": comment.comment_body,
                "detected_products": comment.detected_products,
                "subreddit": comment.subreddit,
                "author": comment.author,
                "score": comment.score,
                "created_utc": comment.timestamp,
                "product_topic": comment.topic,
            }
            for comment in comment_list
        ]

        with self.db_pool.connection() as conn:
            batch_insert_raw_comments(conn, comment_dicts, logger=self.logger)

    def _process_comment_for_all_topics(
        self, comment: Comment, batch_comments: list[ProcessedRedditComment]
    ) -> tuple[int, int]:
        """Process a single comment across all topics"""
        processed_count, inserted_count = 0, 0

        for topic in self._topic_list:
            if not self._should_continue_processing("topic"):
                break

            # Look up the pre-built detector for this topic
            detector = self._detectors.get(topic.upper().strip())
            processed_comment = self._process_comment(comment, detector, topic)

            if processed_comment:
                processed_count += 1
                batch_comments.append(processed_comment)

                new_batch, flushed = self._flush_batch_if_needed(batch_comments)
                batch_comments[:] = new_batch
                inserted_count += flushed

        return processed_count, inserted_count

    def _process_single_post(
        self, post: Submission, batch_comments: list[ProcessedRedditComment]
    ) -> tuple[int, int]:
        """Process all comments from a single post"""
        comments = fetch_comments(post, self.logger)
        processed_count, inserted_count = 0, 0

        for comment in comments:
            if not self._should_continue_processing("comment"):
                break

            comment_processed, comment_inserted = self._process_comment_for_all_topics(
                comment, batch_comments
            )

            processed_count += comment_processed
            inserted_count += comment_inserted

        return processed_count, inserted_count

    def _process_all_posts(
        self, posts: list[Submission], batch_comments: list[ProcessedRedditComment]
    ) -> dict[str, int]:
        """Process all posts and return statistics"""
        stats = {"posts": 0, "comments": 0, "inserted": 0}

        for post in posts:
            if not self._should_continue_processing("post"):
                break

            stats["posts"] += 1
            post_comments, post_inserted = self._process_single_post(post, batch_comments)
            stats["comments"] += post_comments
            stats["inserted"] += post_inserted

        # flush remaining batch to db
        _, final_inserted = self._flush_batch_if_needed(batch_comments, force=True)
        stats["inserted"] += final_inserted

        return stats

    def _run_ingestion_pipeline(self) -> IngestionResult:
        """
        Main orchestrator function: fetch, process, and publish comments

        Returns:
            IngestionResult with counts of posts/comments processed
        """
        all_posts = self._fetch_all_posts()
        batch_comments: list[ProcessedRedditComment] = []

        stats = self._process_all_posts(all_posts, batch_comments)

        return IngestionResult(
            posts_processed=stats.get("posts", 0),
            comments_processed=stats.get("comments", 0),
            comments_inserted=stats.get("inserted", 0),
            cancelled=self.cancel_requested,
        )

    def _should_continue_processing(self, level: str) -> bool:
        """
        Check if processing should continue or has been cancelled

        Args:
            level: Description of processing level, like post, comment, topic

        Returns:
            True if processing should continue, False if cancelled
        """
        if self.cancel_requested:
            self.logger.info(
                event_type="ingestion_service run",
                message=f"Cancellation requested, stopping at {level} level",
            )
            return False
        return True

    def _flush_batch_if_needed(
        self, batch: list[ProcessedRedditComment], force: bool = False
    ) -> tuple[list[ProcessedRedditComment], int]:
        """
        Flush batch of processed comments if size threshold reached or forced

        Args:
            batch: List of comments to potentially flush
            force: If true, flush regardless of batch size

        Returns:
            Tuple of (empty_batch, num_inserted)
        """
        should_flush = force or len(batch) >= self._batch_size

        if not should_flush or not batch:
            return batch, 0

        self._batch_insert_to_db(batch)
        inserted_count = len(batch)

        return [], inserted_count
