from src.schemas.comment import top_comment
from src.schemas.product import RankedProduct
from src.schemas.product import ViewMoreProduct
from src.schemas.product import ProductName
from pydantic import BaseModel

class GetAllCategoriesResponse(BaseModel):
    """Api response for /api/v1/categories endpoint"""
    categories: list[str]

class GetRankedProductsResponse(BaseModel):
    """Api response for /api/v1/categories/products endpoint"""
    products: list[RankedProduct]

class GetViewMoreProductsMetadataResponse(BaseModel):
    """Api response for /api/v1/products/{name}/details endpoint"""
    product: ViewMoreProduct | None

class GetTopCommentsProductResponse(BaseModel):
    """Api response for /api/v1/products/{name}/top_comments endpoint"""
    top_comments: list[top_comment] | None

class GetProductResponse(BaseModel):
    """Api response for /api/v1/products/search?q={query} endpoint"""
    products: list[ProductName] | None