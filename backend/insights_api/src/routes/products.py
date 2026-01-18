from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Request
from fastapi import Depends
from fastapi import APIRouter
from fastapi import HTTPException
from src.core.settings import Settings
from src.schemas.request import GetViewMoreProductMetadataRequest
from src.schemas.request import GetTopCommentsProductRequest
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
    body: GetViewMoreProductMetadataRequest, 
    session: AsyncSession = Depends(get_session)
) -> GetViewMoreProductsMetadataResponse:
    """
    Called when the view more tab is clicked for a product, shows additional metadata like
    Sentiment Breakdown (positive, neutral, negative comment counts), sentiment over time etc
    """
    product_name: str = body.product_name
    time_window: str = body.time_window

    if not product_name:
        raise HTTPException(status_code=400, detail="Missing product_name in request body")
    
    if not time_window:
        raise HTTPException(status_code=400, detail="Missing time_window in request body")

    product_metadata = fetch_view_more_products_metadata(session, product_name, time_window)

    return GetViewMoreProductsMetadataResponse(product=product_metadata)

@routes.get(path="/products/top_comments/{name}", response_model=GetTopCommentsProductResponse)
async def get_products_top_comments(
    body: GetTopCommentsProductRequest, 
    session: AsyncSession = Depends(get_session)
) -> GetTopCommentsProductResponse:
    """
    Get top comments for the specific comment

    Returns:
        a list of the top comments with the comment text, link, and score
    """
    product_name: str = body.product_name
    time_window: str = body.time_window

    if not product_name:
        raise HTTPException(status_code=400, detail="Missing product_name in request body")
    
    if not time_window:
        raise HTTPException(status_code=400, detail="Missing time_window in request body")

    top_comments = await fetch_top_comments_for_product(session, product_name, time_window)

    return GetTopCommentsProductResponse(top_comments=top_comments)

@routes.get(path="/products/search?q={query}", response_model=GetProductResponse)
async def get_product_by_name(
    query: str, 
    session: AsyncSession = Depends(get_session)
) -> GetProductResponse:
    """Search top 10 matching product names with query"""
    if not query:
        raise HTTPException(status_code=400, detail="Missing search query")

    product_list = await fetch_matching_product_name(session, query)

    return GetProductResponse(products=product_list or [])