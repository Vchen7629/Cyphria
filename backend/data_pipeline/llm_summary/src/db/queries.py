from typing import Any
import psycopg
from psycopg import sql

def fetch_unique_products(
    db_conn: psycopg.Connection, 
    time_window: str,
    min_comments: int = 10
) -> list[str]:
    """
    Fetch unique product names that have sufficient comments for use for summarization

    Args:
        db_conn: psycopg database connection
        time_window: time window of comments to fetch, either 90d or all time
        min_comments: minimum amount of comments that the product needs to have
    
    Returns:
        a list of unique product names
    """ 
    if not time_window:
        return []

    normalized_time_window: str = time_window.lower().strip()

    if not normalized_time_window:
        return []

    params: dict[str, Any] = {"min_comments": min_comments}

    if normalized_time_window == "all_time":
        time_filter = sql.SQL("")
    else:
        time_filter = sql.SQL("WHERE created_utc >= NOW() - %(time_window)s::INTERVAL")
        params["time_window"] = time_window

    query = sql.SQL("""
        SELECT ps.product_name, COUNT(*) as comment_count
        FROM product_sentiment ps
        {time_filter}
        GROUP BY ps.product_name
        HAVING COUNT(*) >= %(min_comments)s
        ORDER BY comment_count DESC
    """).format(time_filter=time_filter)

    with db_conn.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return [row[0] for row in rows]

def fetch_top_comments_for_product(
    db_conn: psycopg.Connection,
    product_name: str,
    time_window: str
) -> list[str]:
    """
    Fetch a list of top processed comments to send to the llm to summarize.
    Returns top 10 positive, top 10 negative, and top 5 neutral comments.

    Args:
        db_conn: psycopg database connection
        product_name: the product we are fetching top comments for
        time_window: time window of comments to fetch, either "90d" or "all_time"

    Returns:
        List of comment body strings (~25 comments total)
    """
    if not product_name or not time_window:
        return []

    normalized_time_window: str = time_window.lower().strip()
    normalized_product_name: str = product_name.strip()

    if not normalized_time_window or not normalized_product_name:
        return []

    params: dict[str, Any] = {"product_name": normalized_product_name}

    if normalized_time_window == "all_time":
        time_filter = sql.SQL("")
    else:
        time_filter = sql.SQL("AND rc.created_utc >= NOW() - %(time_window)s::INTERVAL")
        params["time_window"] = time_window

    query = sql.SQL("""
        WITH ranked_comments AS (
            SELECT
                rc.comment_body,
                CASE
                    WHEN ps.sentiment_score > 0.2 THEN 'positive'
                    WHEN ps.sentiment_score < -0.2 THEN 'negative'
                    ELSE 'neutral'
                END AS sentiment_category,
                ROW_NUMBER() OVER (
                    PARTITION BY CASE
                        WHEN ps.sentiment_score > 0.2 THEN 'positive'
                        WHEN ps.sentiment_score < -0.2 THEN 'negative'
                        ELSE 'neutral'
                    END
                    ORDER BY rc.score DESC
                ) AS rn
            FROM raw_comments rc
            JOIN product_sentiment ps ON rc.comment_id = ps.comment_id
            WHERE %(product_name)s = ANY(rc.detected_products)
            {time_filter}
        )
        SELECT comment_body
        FROM ranked_comments
        WHERE (sentiment_category = 'positive' AND rn <= 10)
           OR (sentiment_category = 'negative' AND rn <= 10)
           OR (sentiment_category = 'neutral' AND rn <= 5)
        ORDER BY
            CASE sentiment_category
                WHEN 'positive' THEN 1
                WHEN 'negative' THEN 2
                WHEN 'neutral' THEN 3
            END,
            rn
    """).format(time_filter=time_filter)

    with db_conn.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return [row[0] for row in rows]

def upsert_llm_summaries(
    db_conn: psycopg.Connection, 
    product_name: str,
    tldr: str,
    time_window: str,
    model_used: str
) -> bool:
    """
    Upsert a llm summary for a product and time window

    Args:
        db_conn: psycopg database connection
        product_name: the product we inserting the summary for
        tldr: the llm generated summary
        time_window: time window of summary to insert for
        model_used: llm used to generate summary

    Returns:
        True if successfully inserted, false otherwise
    """
    input_params = [product_name, tldr, time_window, model_used]

    if not all(input_params):
        return False

    query = """
        INSERT INTO product_summaries (
            product_name, tldr, 
            time_window, model_used
        )
        VALUES (
            %(product_name)s, %(tldr)s,
            %(time_window)s, %(model_used)s
        )
        ON CONFLICT (product_name, time_window)
        DO UPDATE SET
            tldr = EXCLUDED.tldr,
            model_used = EXCLUDED.model_used,
            generated_at = NOW();
    """
    params = {
        "product_name": product_name,
        "tldr": tldr,
        "time_window": time_window,
        "model_used": model_used
    }

    with db_conn.cursor() as cursor:
        cursor.execute(query, params)
        rows_affected = cursor.rowcount

    return rows_affected > 0
