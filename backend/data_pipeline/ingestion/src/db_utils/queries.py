from typing import Any
from typing import Optional
from shared_core.logger import StructuredLogger
from shared_db.retry import retry_with_backoff
import psycopg


def batch_insert_raw_comments(
    conn: psycopg.Connection,
    comments: list[dict[str, Any]],
    logger: Optional[StructuredLogger] = None,
) -> None:
    """
    Batch insert multiple raw comments to the bronze layer for better performance.
    Uses retry logic with exponential backoff for transient database errors.

    Args:
        conn: psycopg3 database connection
        comments: list of comment dictionaries with keys:
            - comment_id (str)
            - post_id (str)
            - comment_body (str)
            - detected_products (list[str])
            - subreddit (str)
            - author (str)
            - score (int)
            - created_utc (datetime)
            - product_topic (str)
        logger: Optional StructuredLogger for logging retry failures

    Example:
        comments = [
            {
                'comment_id': 'abc123',
                'post_id': 'xyz789',
                'comment_body': 'Great GPU!',
                'detected_products': ['NVIDIA RTX 4090'],
                'subreddit': 'nvidia',
                'author': 'user123',
                'score': 42,
                'created_utc': datetime.now(),
                'product_topic': 'GPU'
            }
        ]
        batch_insert_raw_comments(conn, comments, logger=my_logger)
    """
    if not comments:
        return

    @retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
    def _insert() -> None:
        query = """
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, FALSE
            )
            ON CONFLICT (comment_id) DO NOTHING;
        """

        with conn.cursor() as cursor:
            cursor.executemany(query, comments)

        conn.commit()

    _insert()
