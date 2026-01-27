from typing import Optional
from fastapi import Query
from fastapi import Depends
from fastapi import Request
from fastapi import APIRouter
from fastapi import HTTPException
from valkey.asyncio import Valkey
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.settings import Settings
from src.core.logger import StructuredLogger
from src.db_utils.pg_conn import get_session
from src.db_utils.cache_conn import get_cache
from src.db_utils.cache_commands import get_cache_value
from src.db_utils.cache_commands import set_cache_value
from src.db_utils.category_queries import fetch_total_products_count
from src.db_utils.category_queries import fetch_top_mentioned_products
from src.db_utils.category_queries import fetch_topic_top_mentioned_products
from src.schemas.product import TopMentionedProduct
from src.schemas.product import CategoryTopMentionedProduct
from src.schemas.response import GetTopicTopMentionProductResponse
from src.schemas.response import GetCategoryTopMentionProductsResponse
from src.middleware.topic_category_mapping import get_topics_for_category

settings = Settings()

routes = APIRouter(prefix=f"/api/{settings.API_VERSION}", tags=["Production"])


@routes.get(
    path="/category/top_mentioned_products",
    response_model=GetCategoryTopMentionProductsResponse,
)
async def get_top_mentioned_products(
    request: Request,
    cache: Valkey | None = Depends(get_cache),
    session: AsyncSession = Depends(get_session),
    category: str = Query(
        ...,
        min_length=1,
        pattern=r"^\S.*$",
        description="Product category to fetch top products for",
    ),
) -> GetCategoryTopMentionProductsResponse:
    """
    Fetches top 6 products with most mention count across all topics in the category
    Uses Valkey caching layer to improve read latency

    Returns:
        a list of the top mentioned products for the category

    Raises:
        a 404 HTTPException if category_topics or products arent fetched/are None
    """
    logger: StructuredLogger = request.app.state.logger
    # cache should live for 30 mins (1800 seconds) since processing happens every 1 hour + processing time
    cache_expiry_s: int = 1800
    cache_key: str = f"category:{category}:top_products"

    category_topics: list[str] = get_topics_for_category(category)
    if not category_topics:
        raise HTTPException(
            status_code=404, detail=f"topics not found for category: {category}"
        )
    # check cache for the top products for category first before calling db
    if cache:
        cached_response = await get_cache_value(
            cache, cache_key, logger, GetCategoryTopMentionProductsResponse
        )
        if cached_response:
            return cached_response

    top_products: Optional[
        list[CategoryTopMentionedProduct]
    ] = await fetch_top_mentioned_products(session, category_topics)
    if not top_products:
        raise HTTPException(
            status_code=404, detail=f"top products not found for category: {category}"
        )
    api_response = GetCategoryTopMentionProductsResponse(products=top_products)
    # If we have cache available, try to cache result
    if cache:
        await set_cache_value(cache, cache_key, api_response, cache_expiry_s, logger)

    return api_response


@routes.get(path="/category/total_products_count")
async def get_total_products_count(
    session: AsyncSession = Depends(get_session),
    category: str = Query(
        ...,
        min_length=1,
        pattern=r"^\S.*$",
        description="Product category to fetch total product numbers for",
    ),
) -> int:
    """
    Fetches the amount of products for the category

    Returns:
        the amount of products for the category
    """
    category_topics: list[str] = get_topics_for_category(category)
    if not category_topics:
        raise HTTPException(
            status_code=404, detail=f"topics not found for category: {category}"
        )

    product_count: int = await fetch_total_products_count(session, category_topics)

    return product_count


@routes.get(path="/category/topic_most_mentioned_product")
async def get_top_mentioned_product_for_topic(
    session: AsyncSession = Depends(get_session),
    product_topic: str = Query(
        ...,
        min_length=1,
        pattern=r"^\S.*$",
        description="Product topic to fetch top products for",
    ),
) -> GetTopicTopMentionProductResponse:
    """
    Fetches top 3 products with most mention count for specific topic when on the category page

    Returns:
        a list of product dicts containing the product name and letter grade

    Raises:
        a 404 exception if no top products are found for the topic
    """
    top_products: Optional[
        list[TopMentionedProduct]
    ] = await fetch_topic_top_mentioned_products(session, product_topic)
    if not top_products:
        raise HTTPException(
            status_code=404,
            detail=f"top products not found for product_topic: {product_topic}",
        )

    return GetTopicTopMentionProductResponse(products=top_products)
