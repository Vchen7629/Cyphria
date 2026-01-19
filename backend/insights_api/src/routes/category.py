from src.core.settings import Settings
from src.db_utils.conn import get_session
from src.db_utils.queries import fetch_ranked_products_for_category
from src.schemas.response import GetAllCategoriesResponse
from src.schemas.response import GetRankedProductsResponse
from fastapi import Depends
from fastapi import APIRouter
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

settings = Settings()

routes = APIRouter(prefix=f"/{settings.API_VERSION}", tags=["Production"])

@routes.get(path="/category", response_model=GetAllCategoriesResponse)
async def get_all_product_categories() -> GetAllCategoriesResponse:
    """
    Route that frontend calls to get all product categories

    Returns:
        a list of all product category strings
    """
    return GetAllCategoriesResponse(
        categories=["Gpus", "Laptops", "Headphones"]
    )

@routes.get(path="/category/products", response_model=GetRankedProductsResponse)
async def get_ranked_products_for_category(
    category: str = Query(..., description="Product category to fetch ranked products for"),
    time_window: str = Query(..., description="Time window filter (e.g. 90d, 30d)"),
    session: AsyncSession = Depends(get_session)
) -> GetRankedProductsResponse:
    """
    Route that frontend calls to get ranked products for specified category
    with their metadata like ranking score, letter, mentions, etc
    """
    ranked_products = await fetch_ranked_products_for_category(session, category, time_window)

    return GetRankedProductsResponse(products=ranked_products)