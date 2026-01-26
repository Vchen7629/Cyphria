from datetime import datetime
from src.schemas.product import SearchProduct
from pydantic import BaseModel

class FetchMatchingProductNameResult(BaseModel):
    """Return value of the FetchMatchingProductName query function"""
    product_list: list[SearchProduct]
    current_page: int
    total_pages: int

class FetchProductSentimentScores(BaseModel):
    """Return value of the fetch_product_sentiment_scores query function"""
    positive_sentiment_count: int
    neutral_sentiment_count: int
    negative_sentiment_count: int

class FetchTopRedditCommentsResult(BaseModel):
    """Return value of fetch_top_reddit_comments query function"""
    comment_body: str
    score: int
    reddit_link: str
    created_utc: datetime

class FetchProductsResult(BaseModel):
    """Return value of fetch_products query function"""
    product_name: str
    grade: str
    bayesian_score: float
    mention_count: int
    approval_percentage: int
    is_top_pick: bool
    is_most_discussed: bool
    has_limited_data: bool
    