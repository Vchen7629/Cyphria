from typing import Literal
from typing import Optional
from fastapi import Query
from fastapi import Depends
from fastapi import Request
from fastapi import APIRouter
from fastapi import HTTPException
from valkey.asyncio import Valkey
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.core.settings import Settings
from src.core.logger import StructuredLogger
from src.schemas.response import SearchProductResponse
from src.schemas.response import GetViewMoreProductsMetadataResponse
from src.schemas.response import GetTopCommentsProductResponse
from src.schemas.queries import FetchProductSentimentScores
from src.schemas.queries import FetchTopRedditCommentsResult
from src.schemas.queries import FetchMatchingProductNameResult
from src.db_utils.pg_conn import get_session
from src.db_utils.cache_conn import get_cache
from src.db_utils.cache_commands import get_cache_value
from src.db_utils.cache_commands import set_cache_value
from src.db_utils.product_queries import fetch_top_reddit_comments
from src.db_utils.product_queries import fetch_matching_product_name
from src.db_utils.product_queries import fetch_product_sentiment_scores

settings = Settings()

routes = APIRouter(prefix=f"/api/{settings.API_VERSION}")

@routes.get(path="/product/sentiment_scores")
async def get_sentiment_scores(
    product_name: str = Query(..., min_length=1, pattern=r"^\S.*$", description="Product name to fetch sentiment scores for"),
    time_window: Literal["all_time", "90d"] = Query(..., description="Time window filter, either 90d or all_time"),
    session: AsyncSession = Depends(get_session)
) -> GetViewMoreProductsMetadataResponse:
    """
    Called when the view more tab is clicked for a product, shows additional metadata like
    Sentiment Breakdown (positive, neutral, negative comment counts), sentiment over time etc

    Returns:
        the counts for positive_sentiment, neutral_sentiment, and negative_sentiment comment mentions

    Raises:
        a 404 HTTPException if sentiment counts are not found for the product and time window
    """

    product_sentiment_scores: Optional[FetchProductSentimentScores] = await fetch_product_sentiment_scores(session, product_name, time_window)
    if not product_sentiment_scores:
        raise HTTPException(
            status_code=404, 
            detail=f"Sentiment counts not found for product: {product_name} time_window: {time_window}"
        )

    return GetViewMoreProductsMetadataResponse(product=product_sentiment_scores)

@routes.get(path="/product/top_comments", response_model=GetTopCommentsProductResponse)
async def get_top_comments(
    request: Request,
    product_name: str = Query(..., min_length=1, pattern=r"^\S.*$", description="Product name to fetch top comments for"),
    time_window: Literal["all_time", "90d"] = Query(..., description="Time window filter (e.g. 90d, 30d)"),
    session: AsyncSession = Depends(get_session),
    cache: Valkey | None = Depends(get_cache)
) -> GetTopCommentsProductResponse:
    """
    Get top comments for the specific product.
    uses Valkey caching layer to improve fetch performance

    Returns:
        a list of the top comments with the comment text, link, score, and created_utc timestamp
    
    Raises:
        a 404 HTTPException if no reddit comments are found for the product and time window
    """
    logger: StructuredLogger = request.app.state.logger
    # cache should live for 30 mins (1800 seconds) since processing happens every 1 hour + processing time
    cache_expiry_s: int = 1800
    cache_key: str = f"product:{product_name}:time_window:{time_window}:top_comments"

    # check cache first before expensive db call
    if cache:
        cached_response = await get_cache_value(cache, cache_key, logger, GetTopCommentsProductResponse)
        if cached_response:
            return cached_response

    top_comments: Optional[list[FetchTopRedditCommentsResult]] = await fetch_top_reddit_comments(session, product_name, time_window)
    if not top_comments:
        raise HTTPException(
            status_code=404, 
            detail=f"No reddit comments found for product: {product_name} and time_window: {time_window}"
        )
    
    api_response = GetTopCommentsProductResponse(top_comments=top_comments)

    # update cache with the new or existing query
    if cache:
        await set_cache_value(cache, cache_key, api_response, cache_expiry_s, logger)

    return api_response

@routes.get(path="/product/search", response_model=SearchProductResponse)
async def get_product_by_name(
    request: Request,
    query: str = Query(..., alias="q", min_length=1, pattern=r"^\S.*$", description="the product name we are trying to find"),
    current_page: int = Query(..., ge=1, description="current api pagination page we are fetching results for"), 
    session: AsyncSession = Depends(get_session),
    cache: Valkey | None = Depends(get_cache),
) -> SearchProductResponse:
    """
    Search all matching product names with query, used in the header searchbar
    uses Valkey caching layer to improve search performance
    
    Returns:
        a list of matching products (product_name, product_topic, grade, mention_count, category), 
        current page and total pages for pagination or an empty array if none found
    """
    logger: StructuredLogger = request.app.state.logger
    search_cache_ttl_s: int = 600 # 10 minutes
    normalized_query: str = query.strip().lower()
    cache_key = f"search:{normalized_query}:page:{current_page}"

    # check cache if someone else already searched this term before hitting db
    if cache:
        cached_response = await get_cache_value(cache, cache_key, logger, SearchProductResponse)
        if cached_response:
            return cached_response

    paginated_search_res: Optional[FetchMatchingProductNameResult] = await fetch_matching_product_name(session, normalized_query, current_page)
    if not paginated_search_res:
        return SearchProductResponse(
            products=[],
            current_page=1,
            total_pages=1
        )

    api_response = SearchProductResponse(
        products=paginated_search_res.product_list,
        current_page=paginated_search_res.current_page,
        total_pages=paginated_search_res.total_pages
    )

    # update cache with search query
    if cache:
        await set_cache_value(cache, cache_key, api_response, search_cache_ttl_s, logger)

    return api_response