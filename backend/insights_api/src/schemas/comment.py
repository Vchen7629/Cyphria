from pydantic import BaseModel

class top_comment(BaseModel):
    """Single top comment containing comment text, link, and score"""
    comment_text: str
    link: str
    score: int

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