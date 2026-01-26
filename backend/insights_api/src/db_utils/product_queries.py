from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.logger import StructuredLogger
from src.db_utils.retry import retry_with_backoff
from src.schemas.queries import FetchProductSentimentScores
from src.schemas.queries import FetchTopRedditCommentsResult
from src.schemas.queries import FetchMatchingProductNameResult
from src.middleware.metrics import db_query_duration
from src.middleware.topic_category_mapping import get_category_for_topic
import time

logger = StructuredLogger(pod="insights_api")

@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_matching_product_name(
    session: AsyncSession, query: str, page: int = 1
) -> Optional[FetchMatchingProductNameResult]:
    """
    Fetch all products matching the search query, pagination with cursor approach.
    Each page will have 6 items

    Args:
        session: temporary db session created for this query
        query: the search query we are matching product name on
        page: the current pagination page of the products search result we are on

    Returns:
        A list of matching dicts containing the product name, product_topic, grade, mention_count, and category
        , the current page, total pages, and booleans to check if theres a next or prev page
    """
    # Escape SQL LIKE/ILIKE wildcards to treat them as literal characters
    escaped_query = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    per_page: int = 6 # results per page

    # get total product count for later use
    total_products_query = text("""
        SELECT COUNT(DISTINCT product_name)
        FROM product_rankings
        WHERE product_name ILIKE '%' || :query || '%' ESCAPE '\\'
    """)

    start_time = time.perf_counter()
    total_products_result = await session.execute(total_products_query, {"query": escaped_query})
    total_products_count = total_products_result.scalar()

    if total_products_count == 0:
        return None

    fetch_matching_products_query = text(f"""
        SELECT product_name, product_topic, grade, mention_count
        FROM product_rankings
        WHERE product_name ILIKE '%' || :query || '%' ESCAPE '\\'
        GROUP BY product_name, product_topic, grade, mention_count
        ORDER BY
            CASE WHEN product_name ILIKE :query || '%' ESCAPE '\\' THEN 0 ELSE 1 END,
            product_name
        LIMIT :limit
        OFFSET :offset
    """)

    offset = (page - 1) * per_page
    result = await session.execute(
        fetch_matching_products_query, 
        {"query": query, "limit": per_page, "offset": offset}
    )
    rows = result.fetchall()
    # Map topic to category using in-memory lookup
    products: list[dict[str, str | int]] = [
        {**row._asdict(), "category": get_category_for_topic(row.product_topic) or "unknown"}
        for row in rows
    ]

    total_pages = (total_products_count + per_page - 1) // per_page if total_products_count else 0
    duration = time.perf_counter() - start_time
    db_query_duration.labels(
        query_type="get", 
        query_name="fetch_matching_product_name", 
        table="product_rankings"
    ).observe(duration)

    return FetchMatchingProductNameResult(
        product_list=products,
        current_page=page,
        total_pages=total_pages
    )

@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_product_sentiment_scores(
    session: AsyncSession, product_name: str, time_window: str
) -> Optional[FetchProductSentimentScores]:
    """
    Fetch sentiment scores for a specific product and time_window

    Args:
        session: temporary db session created for this query
        product_name: the product name we are fetching metadata for
        time_window: the time_window we want rankings for (90d or all_time)

    Returns:
        A product dict containing the sentiment scores
    """
    query = text("""
        SELECT positive_count, neutral_count, negative_count
        FROM product_rankings
        WHERE LOWER(product_name) = LOWER(:product_name)
        AND time_window = :time_window
    """)

    start_time = time.perf_counter()
    result = await session.execute(
        query,
        {
            "product_name": product_name.strip(),
            "time_window": time_window
        }
    )
    row = result.fetchone()
    if not row:
        return None

    duration = time.perf_counter() - start_time
    db_query_duration.labels(
        query_type="get",
        query_name="fetch_product_sentiment_scores",
        table="product_rankings"
    ).observe(duration)
    
    return FetchProductSentimentScores(
        positive_sentiment_count=row.positive_count,
        neutral_sentiment_count=row.neutral_count,
        negative_sentiment_count=row.negative_count
    )

@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_top_reddit_comments(
    session: AsyncSession, product_name: str, time_window: str
) -> Optional[list[FetchTopRedditCommentsResult]]:
    """
    Fetch the top 5 reddit comments (highest scores) for a product in a time window

    Args:
        session: temporary db session created for this query
        product_name: the product name we are fetching metadata for
        time_window: the time_window we want rankings for (90d or all_time)

    Returns:
        A list of comment dicts containing comment text, upvotes, link, and the created
        timestamp for the comment otherwise none
    """
    base_query = """
        SELECT
            comment_body AS comment_text,
            score,
            'https://reddit.com/comments/' || comment_id AS link,
            created_utc
        FROM raw_comments
        WHERE LOWER(:product_name) = ANY(SELECT LOWER(unnest(detected_products)))
        AND sentiment_processed = TRUE
    """

    if time_window.lower().strip() == "90d":
        base_query += " AND created_utc >= NOW() - INTERVAL '90 days'"

    base_query += " ORDER BY score DESC LIMIT 5;"
    
    start_time = time.perf_counter()
    result = await session.execute(text(base_query), {"product_name": product_name.strip()})
    rows = result.fetchall()
    if not rows:
        return None
    
    duration = time.perf_counter() - start_time
    db_query_duration.labels(
        query_type="get", 
        query_name="fetch_top_reddit_comments", 
        table="raw_comments"
    ).observe(duration)

    return [
        FetchTopRedditCommentsResult(
            comment_body=row.comment_text,
            score=row.score,
            reddit_link=row.link,
            created_utc=row.created_utc
        )
        for row in rows
    ]
