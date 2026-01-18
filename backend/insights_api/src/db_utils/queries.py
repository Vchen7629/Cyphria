from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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