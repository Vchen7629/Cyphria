from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.logger import StructuredLogger
from src.db_utils.retry import retry_with_backoff
from src.schemas.queries import FetchProductsResult
from src.middleware.metrics import db_query_duration
from datetime import datetime, timezone, timedelta
import time

logger = StructuredLogger(pod="insights_api")


@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_total_products_ranked(session: AsyncSession, product_topic: str) -> int:
    """
    Fetch number of products ranked for a specific topic

    Args:
        session: temporary db session created for this query
        product_topic: the product_topic we finding are the count for

    Returns:
        the number of products ranked for that topic
    """
    query = text("""
        SELECT COUNT(*)
        FROM product_rankings 
        WHERE LOWER(product_topic) = LOWER(:product_topic)
    """)

    start_time = time.perf_counter()
    result = await session.execute(query, {"product_topic": product_topic.strip()})
    duration = time.perf_counter() - start_time
    db_query_duration.labels(
        query_type="get",
        query_name="fetch_topic_total_products_ranked",
        table="product_rankings",
    ).observe(duration)

    return result.scalar() or 0


@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_total_comments(
    session: AsyncSession, product_topic: str, time_window: str
) -> int:
    """
    Fetch number of comments that contribute to product scores for this specific topic

    Args:
        session: temporary db session created for this query
        product_topic: the product_topic we are finding total mention count for
        time_window: 90d or all_time

    Returns:
        the number of comments that contribute to product scores or 0 if none found
    """
    normalized_time_window: str = time_window.lower().strip()
    normalized_product_topic: str = product_topic.lower().strip()

    if not normalized_time_window or normalized_time_window == "":
        return 0

    if not normalized_product_topic or normalized_product_topic == "":
        return 0

    if normalized_time_window == "all_time":
        query = text("""
            SELECT COUNT(*)
            FROM raw_comments
            WHERE LOWER(product_topic) = :product_topic
            AND sentiment_processed = TRUE;
        """)
        params = {"product_topic": normalized_product_topic}
    else:
        days = int(normalized_time_window.replace("d", ""))
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        query = text("""
            SELECT COUNT(*)
            FROM raw_comments
            WHERE LOWER(product_topic) = :product_topic
            AND sentiment_processed = TRUE
            AND created_utc >= :cutoff_date;
        """)
        params = {"product_topic": normalized_product_topic, "cutoff_date": cutoff_date}

    start_time = time.perf_counter()
    result = await session.execute(query, params)
    duration = time.perf_counter() - start_time
    db_query_duration.labels(
        query_type="get", query_name="fetch_topic_total_comments", table="raw_comments"
    ).observe(duration)

    return result.scalar() or 0


@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_products(
    session: AsyncSession, product_topic: str, time_window: str
) -> Optional[list[FetchProductsResult]]:
    """
    Fetch all products for a product_topic on a time_window from the database

    Args:
        session: temporary db session created for this query
        product_topic: the product_topic we are fetching products from
        time_window: the time_window we want rankings for (90d or all_time)

    Returns:
        list of product dicts containing the metadata or None if none are fetched
    """
    query = text("""
        SELECT 
            product_name, grade, bayesian_score, mention_count, approval_percentage,
            is_top_pick, is_most_discussed, has_limited_data
        FROM product_rankings 
        WHERE LOWER(product_topic) = LOWER(:product_topic)
        AND LOWER(time_window) = :time_window
        ORDER BY rank ASC;
    """)

    start_time = time.perf_counter()
    result = await session.execute(
        query, {"product_topic": product_topic.strip(), "time_window": time_window}
    )
    rows = result.fetchall()
    if not rows:
        return None

    duration = time.perf_counter() - start_time
    db_query_duration.labels(
        query_type="get", query_name="fetch_topic_products", table="product_rankings"
    ).observe(duration)

    return [
        FetchProductsResult(
            product_name=row.product_name,
            grade=row.grade,
            bayesian_score=row.bayesian_score,
            mention_count=row.mention_count,
            approval_percentage=row.approval_percentage,
            is_top_pick=row.is_top_pick,
            is_most_discussed=row.is_most_discussed,
            has_limited_data=row.has_limited_data,
        )
        for row in rows
    ]
