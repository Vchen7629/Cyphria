from typing import Any
from typing import Optional
from praw import Reddit
from praw.models import Comment
from praw.models import Submission
from psycopg_pool.pool import ConnectionPool
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.api.job_state import JobState
from src.api.schemas import IngestionResult
from src.api.schemas import ProcessedRedditComment
from src.core.logger import StructuredLogger
from src.utils.fetch_comments import fetch_comments
from src.utils.fetch_post import fetch_post_delayed
from src.db_utils.queries import batch_insert_raw_comments
from src.preprocessing.demojify import demojify
from src.preprocessing.url_remover import remove_url
from src.preprocessing.check_english import detect_english
from src.preprocessing.is_valid_comment import is_valid_comment
from src.preprocessing.relevant_fields import extract_relevant_fields
from src.product_utils.detector_factory import ProductDetectorWrapper
import prawcore


class IngestionService:
    """Ingestion service that processes Reddit Comments and filters for valid comments"""

    def __init__(
        self,
        reddit_client: Reddit,
        db_pool: ConnectionPool,
        logger: StructuredLogger,
        topic_list: list[str],
        subreddit_list: list[str],
        detector_list: list[ProductDetectorWrapper],
        normalizer: Any,
        fetch_executor: ThreadPoolExecutor,
    ) -> None:
        self.reddit_client = reddit_client
        self.db_pool = db_pool
        self.logger = logger
        self.topic_list = topic_list
        self.subreddit_list = subreddit_list
        self.detector_list = detector_list
        self.normalizer = normalizer
        self.fetch_executor = fetch_executor

        # cancellation flag, used to request graceful shutdown
        self.cancel_requested = False

    def _fetch_all_posts(self) -> list[Submission]:
        """
        Fetch posts from all subreddits with per-subreddit error handling

        Returns:
           all_posts: list containing reddit post submission objects
        """
        all_posts = []

        for subreddit in self.subreddit_list:
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
        self, comment: Comment, detector: ProductDetectorWrapper, topic: str
    ) -> ProcessedRedditComment | None:
        """
        Extract, transform, and filter a comment

        Args:
            comment: single Praw reddit comment object
            detector: a product detector used for a product topic
            topic: the product topic we are trying to process for

        Returns:
            ProcessedRedditComment: Pydantic data object with relevant fields from the
                        comment like post_id, text, author, timestamp, upvotes
            None: none is returned if the comment is invalid
        """
        if not is_valid_comment(comment):
            return None

        # if the comment doesnt contain a product name we should skip it
        if not detector.contains_product(comment.body):
            return None

        products_in_comment: list[str] = detector.extract_products(comment.body)
        normalized_product_name: list[str] = self.normalizer.normalize(topic, products_in_comment)

        # extracting only relevant parts of the comment api res
        extracted: ProcessedRedditComment = extract_relevant_fields(
            comment, normalized_product_name
        )
        url_removed: str = remove_url(extracted.comment_body)
        demojified: str = demojify(url_removed)

        lang: str | None = detect_english(url_removed)
        if lang != "en":  # If the post is non-english skip it
            return None

        return ProcessedRedditComment(
            comment_id=extracted.comment_id,
            comment_body=demojified,
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

    def _run_ingestion_pipeline(self) -> IngestionResult:
        """
        Main orchestrator function: fetch, process, and publish comments

        Returns:
            IngestionResult with counts of posts/comments processed
        """
        all_posts = self._fetch_all_posts()
        batch_comments: list[Any] = []

        posts_processed = 0
        comments_processed = 0
        comments_inserted = 0

        for post in all_posts:
            if self.cancel_requested:
                self.logger.info(
                    event_type="ingestion_service run",
                    message="Cancellation requested, stopping at post level",
                )
                break

            comments: list[Comment] = fetch_comments(post, self.logger)
            posts_processed += 1

            for comment in comments:
                if self.cancel_requested:
                    self.logger.info(
                        event_type="ingestion_service run",
                        message="Cancellation requested, stopping at comment level",
                    )
                    break

                for topic, detector in zip(self.topic_list, self.detector_list):
                    if self.cancel_requested:
                        self.logger.info(
                            event_type="ingestion_service run",
                            message="Cancellation requested, stopping at comment level",
                        )
                        break

                    processed_comment: Optional[ProcessedRedditComment] = self._process_comment(
                        comment, detector, topic
                    )
                    if not processed_comment:
                        continue

                    comments_processed += 1
                    batch_comments.append(processed_comment)

                if len(batch_comments) >= 100:
                    self._batch_insert_to_db(batch_comments)
                    comments_inserted += len(batch_comments)
                    batch_comments = []

        # this ensures remaining comments after loops are written to the db
        if batch_comments:
            self._batch_insert_to_db(batch_comments)
            comments_inserted += len(batch_comments)
            batch_comments = []

        return IngestionResult(
            posts_processed=posts_processed,
            comments_processed=comments_processed,
            comments_inserted=comments_inserted,
            cancelled=self.cancel_requested,
        )

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
