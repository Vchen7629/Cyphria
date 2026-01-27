from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.db_utils.retry import retry_with_backoff
from src.core.logger import StructuredLogger
from src.middleware.metrics import db_query_duration
from src.schemas.product import TopMentionedProduct
from src.schemas.product import CategoryTopMentionedProduct
import time

logger = StructuredLogger(pod="insights_api")


@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_top_mentioned_products(
    session: AsyncSession, category_topics: list[str]
) -> Optional[list[CategoryTopMentionedProduct]]:
    """
    Fetch top 6 most mentioned products across all topics for a category from the database

    Args:
        session: temporary db session created for this query
        category_topics: the list of product_topics belonging to the category like ["GPU", "Laptop"]

    Returns:
        list of top mentioned product containing name, mention count, letter grade, and topic its from
        or none if no rows match
    """
    query = text("""
        SELECT product_name, grade, mention_count, product_topic 
        FROM product_rankings
        WHERE UPPER(product_topic) = ANY(:topic_list)
        ORDER BY mention_count DESC
        LIMIT 6
    """)

    start_time = time.perf_counter()
    result = await session.execute(query, {"topic_list": category_topics})
    rows = result.fetchall()

    if not rows:
        logger.debug(
            event_type="insights_api run", message="top mention products not fetched"
        )
        return None

    duration = time.perf_counter() - start_time
    db_query_duration.labels(
        query_type="get",
        query_name="fetch_category_top_mentioned_products",
        table="product_rankings",
    ).observe(duration)

    return [
        CategoryTopMentionedProduct(
            product_name=row.product_name,
            grade=row.grade,
            mention_count=row.mention_count,
            topic_name=row.product_topic,
        )
        for row in rows
    ]


@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_topic_top_mentioned_products(
    session: AsyncSession, product_topic: list[str]
) -> Optional[list[TopMentionedProduct]]:
    """
    Fetch top 3 most mentioned products across specific topics for a category from the database

    Args:
        session: temporary db session created for this query
        product_topic: the product_topic  like "GPU", "Laptop"

    Returns:
        list of top mentioned 3 product containing name, and letter grade or none if no rows match
    """
    query = text("""
        SELECT product_name, grade
        FROM product_rankings
        WHERE UPPER(product_topic) = :product_topic
        ORDER BY mention_count DESC
        LIMIT 3
    """)

    start_time = time.perf_counter()
    result = await session.execute(query, {"product_topic": product_topic})
    rows = result.fetchall()

    if not rows:
        logger.debug(
            event_type="insights_api run", message="top mention products not fetched"
        )
        return None
    duration = time.perf_counter() - start_time
    db_query_duration.labels(
        query_type="get",
        query_name="fetch_category_topic_mentioned_products",
        table="product_rankings",
    ).observe(duration)

    return [
        TopMentionedProduct(product_name=row.product_name, grade=row.grade)
        for row in rows
    ]


@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_total_products_count(
    session: AsyncSession, topic_list: list[str]
) -> int:
    """
    Fetch number of products for the category

    Args:
        session: temporary db session created for this query
        topic_list: the list of product_topics that match products

    Returns:
        the number of products ranked for that category
    """
    query = text("""
        SELECT COUNT(*)
        FROM product_rankings
        WHERE UPPER(product_topic) = ANY(:topic_list)
    """)

    start_time = time.perf_counter()
    result = await session.execute(query, {"topic_list": topic_list})
    duration = time.perf_counter() - start_time
    db_query_duration.labels(
        query_type="get",
        query_name="fetch_category_total_products_count",
        table="product_rankings",
    ).observe(duration)

    return result.scalar() or 0
