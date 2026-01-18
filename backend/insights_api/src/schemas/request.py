from pydantic import BaseModel

class GetRankedProductsRequest(BaseModel):
    """Api request body for /api/v1/categories/products endpoint"""
    category: str
    time_window: str
