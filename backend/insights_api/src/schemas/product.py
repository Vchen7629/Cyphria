from pydantic import BaseModel

class RankedProduct(BaseModel):
    """Single ranked product fetched from the /api/v1/categories/{category}/products endpoint"""
    product_name: str
    grade: str
    bayesian_score: float
    mention_count: int
    approval_percentage: int
    is_top_pick: bool
    is_most_discussed: bool
    has_limited_data: bool

class ViewMoreProduct(BaseModel):
    """Single product metadata fetched from /api/v1/products/view_more"""
    positive_count: int
    neutral_count: int
    negative_count: int

class ProductName(BaseModel):
    """Single product name"""
    product_name: str