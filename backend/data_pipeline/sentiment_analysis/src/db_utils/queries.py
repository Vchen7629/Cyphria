import psycopg
from psycopg.rows import dict_row
from src.api.schemas import UnprocessedComment
from src.api.schemas import ProductSentiment
from src.core.logger import StructuredLogger
from src.db_utils.retry import retry_with_backoff

structured_logger = StructuredLogger(pod="idk")

@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=structured_logger)
def fetch_unprocessed_comments(conn: psycopg.Connection, category: str, batch_size: int = 100) -> list[UnprocessedComment]:
    """
    Fetch a batch of unprocessed comments for a category from the raw_comments table
    for further processing with this worker

    Args:
        conn: psycopg3 database connection
        category: the product category we are fetching the comments for
        batch_size: number of comments to fetch per batch

    Returns:
        list of dicts with the comment metadata:
            - comment_id
            - comment_body
            - category
            - detected_products (array)
            - created_utc
    """
    query = """
        SELECT
            comment_id,
            comment_body,
            category,
            detected_products,
            created_utc
        FROM raw_comments
        WHERE sentiment_processed = FALSE
        AND UPPER(TRIM(category)) = UPPER(TRIM(%s))
        ORDER BY created_utc ASC
        LIMIT %s
    """

    normalized_category = category.strip().upper()

    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query, (normalized_category, batch_size))
        results = cursor.fetchall()

    return [UnprocessedComment.model_validate(row) for row in results]

@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=structured_logger)
def batch_insert_product_sentiment(conn: psycopg.Connection, sentiments: list[ProductSentiment]) -> int:
    """
    Batch insert multiple processed product sentiments to the product sentiment table (silver layer).

    Args:
        conn: psycopg3 database connection
        comments: list of comment dictionaries with keys:
            - comment_id (str): ID of the source comment
            - product_name (str): normalized product name
            - category (str): the category of the product
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
            category,
            sentiment_score,
            created_utc
        ) VALUES (
            %(comment_id)s,
            %(product_name)s,
            %(category)s,
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