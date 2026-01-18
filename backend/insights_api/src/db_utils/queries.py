from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.db_utils.retry import retry_with_backoff
from src.core.logger import StructuredLogger

logger = StructuredLogger(pod="insights_api")

@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_ranked_products_for_category(
    session: AsyncSession, category: str, time_window: str
) -> list[dict[str, str | int | float | bool]]:
    """
    Fetch all ranking products for a category on a time_window from the database

    Args:
        session: temporary db session created for this query
        category: the category we are fetching products from
        time_window: the time_window we want rankings for (90d or all_time)

    Returns:
        list of product dicts containing the metadata
    """
    query = text("""
        SELECT 
            product_name, grade, bayesian_score, mention_count, approval_percentage,
            is_top_pick, is_most_discussed, has_limited_data
        FROM product_rankings 
        WHERE category = :category
        AND time_window = :time_window
        ORDER BY rank DESC;
    """)

    result = await session.execute(
        query,
        {
            "category": category,
            "time_window": time_window
        }
    )
    rows = result.fetchall()

    return [row._asdict() for row in rows]

@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_view_more_products_metadata(
    session: AsyncSession, product_name: str, time_window: str
) -> dict[str, int] | None:
    """
    Fetch all ranking products for a category on a time_window from the database

    Args:
        session: temporary db session created for this query
        product_name: the product name we are fetching metadata for
        time_window: the time_window we want rankings for (90d or all_time)

    Returns:
        A product dict containing view more metadata or None if it doesnt exist
    """
    query = text("""
        SELECT positive_count, neutral_count, negative_count
        FROM product_rankings 
        WHERE product_name = :product_rank
        AND time_window = :time_window
    """)

    result = await session.execute(
        query,
        {
            "product_name": product_name,
            "time_window": time_window
        }
    )
    row = result.fetchone()

    return row._asdict() if row else None

@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_top_comments_for_product(
    session: AsyncSession, product_name: str, time_window: str
) -> list[dict[str, int]]:
    """
    Fetch the top 5 comments (highest scores) for a product in a time window

    Args:
        session: temporary db session created for this query
        product_name: the product name we are fetching metadata for
        time_window: the time_window we want rankings for (90d or all_time)

    Returns:
        A list of product dicts containing comment text, upvotes, and link to comment
    """
    base_query = """
        SELECT comment_body, score, comment_id
        FROM raw_comments
        WHERE :product_name = ANY(detected_products)
        AND sentiment_processed = TRUE
    """

    if time_window.lower().strip() == "90d":
        base_query += " AND created_utc >= NOW() - INTERVAL '90 days'"

    base_query += " ORDER BY score DESC LIMIT 5;"

    result = await session.execute(text(base_query), {"product_name": product_name})
    rows = result.fetchall()

    return [row._asdict() for row in rows]

@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=logger)
async def fetch_matching_product_name(session: AsyncSession, query: str) -> list[dict[str, str]] | None:
    """
    Fetch top 10 products matching the search query

    Args:
        session: temporary db session created for this query
        query: the search query we are matching product name on

    Returns:
        A list of matching dicts containing the product names matching the query
    """
    base_query = text("""
        SELECT DISTINCT product_name
        FROM product_rankings
        WHERE product_name ILIKE '%' || :query || '%'
        ORDER BY
            CASE WHEN product_name ILIKE :query || '%' THEN 0 ELSE 1 END,
            product_name
        LIMIT 10
    """)

    result = await session.execute(base_query, {"query": query})
    rows = result.fetchall()

    return [row._asdict() for row in rows]


