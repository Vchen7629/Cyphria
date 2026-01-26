from pydantic import BaseModel
from src.schemas.product import SearchProduct
from src.schemas.product import RankedProduct
from src.schemas.product import ViewMoreProduct
from src.schemas.product import TopMentionedProduct
from src.schemas.product import CategoryTopMentionedProduct
from src.schemas.comment import top_comment

class GetCategoryTopMentionProductsResponse(BaseModel):
    """Api response for /api/v1/category/top_mentioned_products"""
    products: list[CategoryTopMentionedProduct]

class GetTopicTopMentionProductResponse(BaseModel):
    """Api response for /api/v1/category/topic_most_mentioned_product"""
    products: list[TopMentionedProduct]

class GetTopicTotalCommentsResponse(BaseModel):
    """Api response for /api/v1/topic/total_comments"""
    total_comment: int

class GetRankedProductsResponse(BaseModel):
    """Api response for /api/v1/category/products endpoint"""
    products: list[RankedProduct] | None

class GetViewMoreProductsMetadataResponse(BaseModel):
    """Api response for /api/v1/products/{name}/details endpoint"""
    product: ViewMoreProduct | None

class GetTopCommentsProductResponse(BaseModel):
    """Api response for /api/v1/products/{name}/top_comments endpoint"""
    top_comments: list[top_comment] | None

class SearchProductResponse(BaseModel):
    """Api response for /api/v1/products/search?q={query} endpoint"""
    products: list[SearchProduct] | None
    current_page: int
    total_pages: int
