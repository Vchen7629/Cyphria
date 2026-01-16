from typing import Any
from src.api.schemas import IngestionResult
from src.product_utils.detector_factory import ProductDetectorWrapper
from psycopg_pool.pool import ConnectionPool
from src.utils.fetch_post import fetch_post_delayed
from src.utils.fetch_comments import fetch_comments
from src.preprocessing.relevant_fields import extract_relevant_fields
from src.preprocessing.url_remover import remove_url
from src.preprocessing.demojify import demojify
from src.preprocessing.is_valid_comment import is_valid_comment
from src.api.schemas import RedditComment
from src.preprocessing.check_english import detect_english
from src.core.logger import StructuredLogger
from src.db_utils.queries import batch_insert_raw_comments
from praw.models import Submission, Comment
from praw import Reddit
import prawcore

class IngestionService:
    """Ingestion service that processes Reddit Comments and filters for valid comments"""
    def __init__(
        self,
        reddit_client: Reddit,
        db_pool: ConnectionPool,
        logger: StructuredLogger,
        category: str,
        subreddits: list[str],
        detector: ProductDetectorWrapper,
        normalizer: Any
    ) -> None:
        self.reddit_client = reddit_client
        self.db_pool = db_pool
        self.logger = logger
        self.category = category
        self.subreddits = subreddits
        self.detector = detector
        self.normalizer = normalizer

        # cancellation flag, used to request graceful shutdown
        self.cancel_requested = False
    
    def _fetch_all_posts(self) -> list[Submission]:
        """
        Fetch posts from all configured subreddits with per-subreddit error handling

        Returns:
           all_posts: list containing reddit post submission objects
        """
        all_posts = []

        for subreddit in self.subreddits:
            try:
                posts = fetch_post_delayed(self.reddit_client, subreddit, self.logger)
                if posts:
                    all_posts.extend(posts)
            except prawcore.exceptions.ServerError as e:
                self.logger.error(
                    event_type="Subreddit Fetch",
                    message=f"Reddit API server error for r/{subreddit}: {e}"
                )
            except Exception as e:
                self.logger.error(
                    event_type="Subreddit Fetch",
                    message=f"Failed to fetch from r/{subreddit}: {e}"
                )
                # python will automatically continue the loop if the exception as thrown

        return all_posts

    def _process_comment(self, comment: Comment) -> RedditComment | None:
        """
        Extract, transform, and filter a comment

        Args:
            comment: single Praw reddit comment object

        Returns:
            RedditComment: Pydantic data object with relevant fields from the
                        comment like post_id, text, author, timestamp, upvotes
            None: none is returned if the comment is invalid
        """
        if not is_valid_comment(comment):
            return None
        
        # if the comment doesnt contain a gpu name or number we should skip it
        if not self.detector.contains_product(comment.body):
            return None
        
        gpus_in_comment: list[str] = self.detector.extract_products(comment.body)
        normalized_gpus: list[str] = self.normalizer.normalize(self.category, gpus_in_comment)

        # extracting only relevant parts of the comment api res
        extracted: RedditComment = extract_relevant_fields(comment, normalized_gpus)
        url_removed: str = remove_url(extracted.comment_body)
        demojified: str = demojify(url_removed)

        lang: str | None = detect_english(url_removed)
        if lang != "en":  # If the post is non-english skip it
            return None
        
        return RedditComment(
            comment_id=extracted.comment_id,
            comment_body=demojified,
            subreddit=extracted.subreddit,
            detected_products=extracted.detected_products,
            timestamp=extracted.timestamp,
            score=extracted.score,
            author=extracted.author,
            post_id=extracted.post_id
        )

    def _batch_insert_to_db(self, comment_list: list[RedditComment]) -> None:
        """
        Method for taking in a batch of valid comments, converting it into a dict, 
        and batch writing to PG table

        Args:
            comment_list: list of reddit comment
        """
        # Convert to dict format expected by batch_insert
        comment_dicts = [
            {
                'comment_id': comment.comment_id,
                'post_id': comment.post_id,
                'comment_body': comment.comment_body,
                'detected_products': comment.detected_products,
                'subreddit': comment.subreddit,
                'author': comment.author,
                'score': comment.score,
                'created_utc': comment.timestamp,
                'category': self.category
            }
            for comment in comment_list
        ]

        with self.db_pool.connection() as conn:
            batch_insert_raw_comments(conn, comment_dicts, logger=self.logger)

    def run(self) -> IngestionResult:
        """
        Main orchestrator function: fetch, process, and publish comments
        
        Returns:
            IngestionResult with counts of posts/comments processed
        """
        all_posts = self._fetch_all_posts()
        batch_comments = []

        posts_processed = 0
        comments_processed = 0
        comments_inserted = 0

        for post in all_posts:
            if self.cancel_requested:
                self.logger.info(
                    event_type="ingestion",
                    message="Cancellation requested, stopping at post level"
                )
                break

            comments: list[Comment] = fetch_comments(post, self.logger)
            posts_processed += 1

            for comment in comments:
                if self.cancel_requested:
                    break
                
                processed_comment: RedditComment | None = self._process_comment(comment)
                comments_processed += 1
                if not processed_comment:
                    continue

                batch_comments.append(processed_comment)

                if len(batch_comments) >= 100:
                    self._batch_insert_to_db(batch_comments)
                    comments_inserted += len(batch_comments)
                    batch_comments = []

        # this ensures remaining comments after loops are written to the db
        if batch_comments:
            self._batch_insert_to_db(batch_comments)
            comments_inserted += len(batch_comments)

        return IngestionResult(
            posts_processed=posts_processed,
            comments_processed=comments_processed,
            comments_inserted=comments_inserted,
            cancelled=self.cancel_requested
        )

if __name__ == "__main__":
    pass
    #for i in range(1):
    #    IngestionService().run()
