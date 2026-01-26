from pydantic import BaseModel

class CategoryTopMentionedProduct(BaseModel):
    """Single top ranked topic fetched from /api/v1/category/top_mentioned_products endpoint"""
    product_name: str
    grade: str
    mention_count: int
    topic_name: str

class TopMentionedProduct(BaseModel):
    """Single top ranked topic fetched from /api/v1/category/topic_topic_mentioned_products endpoint"""
    product_name: str
    grade: str

class RankedProduct(BaseModel):
    """Single ranked product fetched from the /api/v1/category/{category}/products endpoint"""
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

class SearchProduct(BaseModel):
    """Single search product"""
    product_name: str
    product_topic: str
    grade: str
    mention_count: int
