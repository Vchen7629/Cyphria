from pydantic import BaseModel

class GetRankedProductsRequest(BaseModel):
    """Api request body for /api/v1/categories/products endpoint"""
    category: str
    time_window: str

class GetViewMoreProductMetadataRequest(BaseModel):
    """Api request body for /api/v1/product/view_more"""
    product_name: str
    time_window: str

class GetTopCommentsProductRequest(BaseModel):
    """Api request body for /api/v1/products/{name}/top_comments endpoint"""
    product_name: str
    time_window: str