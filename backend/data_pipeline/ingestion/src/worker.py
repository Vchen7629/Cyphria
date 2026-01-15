from src.utils.fetch_post import fetch_post_delayed
from src.utils.fetch_comments import fetch_comments
from src.utils.category_to_subreddit_mapping import category_to_subreddit_mapping
from src.preprocessing.relevant_fields import extract_relevant_fields
from src.preprocessing.url_remover import remove_url
from src.preprocessing.demojify import demojify
from src.preprocessing.is_valid_comment import is_valid_comment
from src.product_utils.detector_factory import DetectorFactory
from src.product_utils.normalizer_factory import NormalizerFactory
from src.core.reddit_client_instance import createRedditClient
from src.core.types import RedditComment
from src.preprocessing.check_english import detect_english
from src.core.logger import StructuredLogger
from src.core.settings_config import settings
from src.db_utils.conn import create_connection_pool
from src.db_utils.queries import batch_insert_raw_comments
from praw.models import Submission, Comment
from praw import Reddit
import prawcore
import signal

class Worker:
    def __init__(self) -> None:
        self.logger = StructuredLogger(pod="data_ingestion")
        self.shutdown_requested = False
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self.reddit_client: Reddit = createRedditClient()
        self.category = settings.product_category
        self.subreddits: list[str] = category_to_subreddit_mapping(self.logger, self.category)
        self.detector = DetectorFactory.get_detector(self.category)
        self.normalizer = NormalizerFactory

        self._database_conn_lifespan()
        self.logger.info(event_type="data ingestion startup", message="Worker init complete")


    def _database_conn_lifespan(self) -> None:
        """
        Method for handling database connection lifespan including creating connection pool,
        and checking the health
        """
        self.logger.info(event_type="data ingestion startup", message="Creating database conenction pool")
        self.db_pool = create_connection_pool()

        # Perform health check for db connection on startup
        self.logger.info(event_type="data ingestion startup", message="Checking Database health check...")
        try:
            with self.db_pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                self.logger.info(event_type="data ingestion startup", message="Database health check passed")
        except Exception as e:
            self.logger.error(event_type="data ingestion startup", message=f"Database health check failed: {e}")
            self.db_pool.close()
            raise 

    def _signal_handler(self, signum: int, _frame: object) -> None:
        """
        Signal handler for graceful shutdown

        Args:
            signum: Signal number
            _frame: Current stack frame (unused but required by signal handler signature)
        """
        signal_name = signal.Signals(signum).name
        self.logger.info(event_type="data ingestion shutdown", message=f"Received {signal_name} signal, initiating graceful shutdown")
        self.shutdown_requested = True
    
    def _cleanup(self) -> None:
        """Cleanup resources on shutdown"""
        self.logger.info(event_type="data ingestion shutdown", message="Cleaning up resources")

        # Close database connection pool
        self.db_pool.close()
        self.logger.info(event_type="data ingestion shutdown", message="Database connection pool closed")

        self.logger.info(event_type="data ingestion shutdown", message="Shutdown complete")

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

    def run(self) -> None:
        """Main orchestrator function: fetch, process, and publish comments"""
        all_posts = self._fetch_all_posts()
        batch_comments = []

        try:            
            for post in all_posts:
                if self.shutdown_requested:
                    break

                comments: list[Comment] = fetch_comments(post, self.logger)
                
                for comment in comments:
                    if self.shutdown_requested:
                        break
                    
                    processed_comment: RedditComment | None = self._process_comment(comment)
                    if not processed_comment:
                        continue

                    batch_comments.append(processed_comment)

                    if len(batch_comments) >= 100:
                        self._batch_insert_to_db(batch_comments)
                        batch_comments = []

            # this ensures remaining comments after loops are written to the db
            if batch_comments:
                self._batch_insert_to_db(batch_comments)
        except Exception as e:
            self.logger.error(event_type="data ingestion worker", message=f"Error in worker loop: {e}")
            raise
        finally:
            self._cleanup()

if __name__ == "__main__":#
    for i in range(1):
        Worker().run()
