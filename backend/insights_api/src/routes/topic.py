from typing import Optional
from typing import Literal
from fastapi import Query
from fastapi import Depends
from fastapi import Request
from fastapi import APIRouter
from fastapi import HTTPException
from valkey.asyncio import Valkey
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.core.settings import Settings
from src.core.logger import StructuredLogger
from src.schemas.queries import FetchProductsResult
from src.schemas.response import GetRankedProductsResponse
from src.schemas.response import GetTopicTotalCommentsResponse
from src.schemas.response import GetTopicTotalProductsRankedResponse
from src.middleware.get_client_ip import get_client_ip
from src.db_utils.pg_conn import get_session
from src.db_utils.cache_conn import get_cache
from src.db_utils.cache_commands import get_cache_value
from src.db_utils.cache_commands import set_cache_value
from src.db_utils.cache_commands import increment_trending_topic
from src.db_utils.topic_queries import fetch_products
from src.db_utils.topic_queries import fetch_total_comments
from src.db_utils.topic_queries import fetch_total_products_ranked
settings = Settings()

routes = APIRouter(prefix=f"/api/{settings.API_VERSION}")

@routes.get(path="/topic/total_products_ranked", response_model=GetTopicTotalProductsRankedResponse)
async def get_topic_total_products_ranked(
    product_topic: str = Query(..., description="Product topic to fetch ranked products for"),
    session: AsyncSession = Depends(get_session)
) -> GetTopicTotalProductsRankedResponse:
    """
    Fetches and returns the number of products ranked for the specified topic
    
    Returns:
        a count number of the total products ranked for the topic
    """
    ranked_count: int = await fetch_total_products_ranked(session, product_topic)
    
    return GetTopicTotalProductsRankedResponse(total_ranked=ranked_count)

@routes.get(path="/topic/total_comments", response_model=GetTopicTotalCommentsResponse)
async def get_topic_total_comments(
    request: Request,
    product_topic: str = Query(..., description="Product topic to fetch ranked products for"),
    time_window: Literal["all_time", "90d"] = Query(..., description="Time window filter, all_time or 90d"),
    session: AsyncSession = Depends(get_session),
    cache: Valkey | None = Depends(get_cache)
) -> GetTopicTotalCommentsResponse:
    """
    Fetches and returns the number of comments that contribute to the 
    product score for the time window and topic

    Returns:
        the count number of the total comments for that product
    """
    logger = request.app.state.logger
    # cache should live for 30 mins (1800 seconds) since processing happens every 1 hour + processing time
    cache_expiry_s: int = 1800
    cache_key: str = f"topic:{product_topic}:total_comments:time_window:{time_window}"

    # check cache before expensive db op
    if cache:
        cached_response = await get_cache_value(cache, cache_key, logger, GetTopicTotalCommentsResponse)
        if cached_response:
            return cached_response

    comment_count: int = await fetch_total_comments(session, product_topic, time_window)
    api_response = GetTopicTotalCommentsResponse(total_comment=comment_count)

    if cache:
        await set_cache_value(cache, cache_key, api_response, cache_expiry_s, logger)

    return api_response

@routes.get(path="/topic/products", response_model=GetRankedProductsResponse)
async def get_ranked_products_for_category(
    request: Request,
    product_topic: str = Query(..., description="Product topic to fetch ranked products for"),
    time_window: Literal["all_time", "90d"] = Query(..., description="Time window filter, either 90d or all_time"),
    session: AsyncSession = Depends(get_session),
    cache: Valkey | None = Depends(get_cache),
    client_ip: str = Depends(get_client_ip)
) -> GetRankedProductsResponse:
    """
    Route that frontend calls to get ranked products for specified topic
    with their metadata like ranking score, letter, mentions, etc
    uses Valkey caching layer to improve fetch performance and increases the view count
    for the current product by one for use in the trending topics feature on homepage

    Returns:
        a list of each product with their metadata or an empty array if none are fetched

    Raises:
        a 404 HTTPException if no products are fetched for the specified topic from the db
    """
    logger: StructuredLogger = request.app.state.logger
    # topic cache should live for 20 mins (1200 seconds) since processing happens every 30 mins + processing time
    topic_cache_expiry_s: int = 1200 
    cache_key: str = f"topic:{product_topic}:top_products:time_window:{time_window}"

    if cache: # check cache before checking database
        cached_response = await get_cache_value(cache, cache_key, logger, GetRankedProductsResponse)
        if cached_response:
            await increment_trending_topic(cache, product_topic, client_ip) # increment the count by 1 for current topic
            return cached_response
    
    ranked_products: Optional[list[FetchProductsResult]] = await fetch_products(session, product_topic, time_window)
    if not ranked_products:
        raise HTTPException(status_code=404, detail=f"No products fetched for the topic: {product_topic}")
    api_response = GetRankedProductsResponse(products=ranked_products)

    # try to update the cache with the ranked products and page view count
    if cache:
        await set_cache_value(
            cache=cache,
            cache_key=cache_key,
            value=api_response,
            ttl_seconds=topic_cache_expiry_s,
            logger=logger,
            on_cache_write=lambda cache: increment_trending_topic(cache, product_topic, client_ip)
        )

    return api_response