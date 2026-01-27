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


class ViewMoreProduct(BaseModel):
    """Single product metadata fetched from /api/v1/products/view_more"""

    positive_sentiment_count: int
    neutral_sentiment_count: int
    negative_sentiment_count: int


class SearchProduct(BaseModel):
    """Single search product"""

    product_name: str
    product_topic: str
    grade: str
    mention_count: int
