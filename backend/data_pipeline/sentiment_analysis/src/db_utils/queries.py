from psycopg.rows import dict_row
from shared_core.logger import StructuredLogger
from shared_db.retry import retry_with_backoff
from src.api.schemas import UnprocessedComment
from src.api.schemas import ProductSentiment
import psycopg

structured_logger = StructuredLogger(pod="sentiment_analysis")


@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=structured_logger)
def fetch_unprocessed_comments(
    conn: psycopg.Connection, product_topic: str, batch_size: int = 100
) -> list[UnprocessedComment]:
    """
    Fetch a batch of unprocessed comments for a product_topic from the raw_comments table
    for further processing with this worker

    Args:
        conn: psycopg3 database connection
        product_topic: the product topic we are fetching the comments for
        batch_size: number of comments to fetch per batch

    Returns:
        list of dicts with the comment metadata:
            - comment_id
            - comment_body
            - product_topic
            - detected_products (array)
            - created_utc
    """
    query = """
        SELECT
            comment_id,
            comment_body,
            product_topic,
            detected_products,
            created_utc
        FROM raw_comments
        WHERE sentiment_processed = FALSE
        AND UPPER(TRIM(product_topic)) = UPPER(TRIM(%s))
        ORDER BY created_utc ASC
        LIMIT %s
    """

    normalized_product_topic = product_topic.strip().upper()

    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query, (normalized_product_topic, batch_size))
        results = cursor.fetchall()

    return [UnprocessedComment.model_validate(row) for row in results]


@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=structured_logger)
def batch_insert_product_sentiment(
    conn: psycopg.Connection, sentiments: list[ProductSentiment]
) -> int:
    """
    Batch insert multiple processed product sentiments to the product sentiment table (silver layer).

    Args:
        conn: psycopg3 database connection
        comments: list of comment dictionaries with keys:
            - comment_id (str): ID of the source comment
            - product_name (str): normalized product name
            - product_topic (str): the product_topic of the product
            - sentiment_score (float): sentiment score from -1 to +1
            - created_utc (str): ISO UTC timestamp when comment was created

    Returns:
        number of rows inserted
    """
    if not sentiments:
        return 0

    query = """
        INSERT INTO product_sentiment (
            comment_id,
            product_name,
            product_topic,
            sentiment_score,
            created_utc
        ) VALUES (
            %(comment_id)s,
            %(product_name)s,
            %(product_topic)s,
            %(sentiment_score)s,
            %(created_utc)s
        )
        ON CONFLICT (comment_id, product_name) DO NOTHING;
    """

    with conn.cursor() as cursor:
        cursor.executemany(query, [s.model_dump() for s in sentiments])
        rows_inserted = cursor.rowcount

    return rows_inserted


@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=structured_logger)
def mark_comments_processed(conn: psycopg.Connection, comment_ids: list[str]) -> int:
    """
    Update the comments that were processed by the sentiment_analysis worker
    by setting the sentiment_processed field in raw_comments table to true

    Args:
        conn: psycopg3 database connection
        comment_ids: list of comment IDs to mark as processed

    Returns:
        number of rows updated
    """
    if not comment_ids:
        return 0

    query = """
        UPDATE raw_comments
        SET sentiment_processed = TRUE
        WHERE comment_id = ANY(%s)
        AND sentiment_processed = FALSE
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (comment_ids,))
        rows_updated = cursor.rowcount

    return rows_updated
