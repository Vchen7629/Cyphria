from typing import Literal
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Depends
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from src.core.settings import Settings
from src.schemas.response import GetViewMoreProductsMetadataResponse
from src.schemas.response import GetTopCommentsProductResponse
from src.schemas.response import GetProductResponse
from src.db_utils.conn import get_session
from src.db_utils.queries import fetch_view_more_products_metadata
from src.db_utils.queries import fetch_top_comments_for_product
from src.db_utils.queries import fetch_matching_product_name

settings = Settings()

routes = APIRouter(prefix=f"/api/{settings.API_VERSION}")

@routes.get(path="/products/view_more")
async def get_view_more_products_metadata(
    product_name: str = Query(..., description="Product name to fetch metadata for"),
    time_window: Literal["all_time", "90d"] = Query(..., description="Time window filter (e.g. 90d, 30d)"),
    session: AsyncSession = Depends(get_session)
) -> GetViewMoreProductsMetadataResponse:
    """
    Called when the view more tab is clicked for a product, shows additional metadata like
    Sentiment Breakdown (positive, neutral, negative comment counts), sentiment over time etc
    """
    product_metadata = await fetch_view_more_products_metadata(session, product_name, time_window)

    return GetViewMoreProductsMetadataResponse(product=product_metadata or None)

@routes.get(path="/products/top_comments", response_model=GetTopCommentsProductResponse)
async def get_products_top_comments(
    product_name: str = Query(..., description="Product name to fetch top comments for"),
    time_window: Literal["all_time", "90d"] = Query(..., description="Time window filter (e.g. 90d, 30d)"),
    session: AsyncSession = Depends(get_session)
) -> GetTopCommentsProductResponse:
    """
    Get top comments for the specific product.

    Returns:
        a list of the top comments with the comment text, link, and score
    """
    top_comments = await fetch_top_comments_for_product(session, product_name, time_window)

    return GetTopCommentsProductResponse(top_comments=top_comments or [])

@routes.get(path="/products/search", response_model=GetProductResponse)
async def get_product_by_name(
    query: str = Query(..., alias="q", min_length=1, description="the product name we are trying to find"), 
    session: AsyncSession = Depends(get_session)
) -> GetProductResponse:
    """Search top 10 matching product names with query"""
    product_list = await fetch_matching_product_name(session, query)

    return GetProductResponse(products=product_list or [])