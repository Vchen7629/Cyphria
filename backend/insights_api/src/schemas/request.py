from pydantic import BaseModel

class GetRankedProductsRequest(BaseModel):
    """Api request for /api/v1/categories/{category}/products endpoint"""
    category: str
    time_window: str
