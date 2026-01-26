from pydantic import BaseModel

class TrendingTopic(BaseModel):
    """Single trending topic item"""
    topic: str
    view_count: int

class TrendingTopicsResponse(BaseModel):
    """Api response for /api/v1/home/trending/product_topics"""
    trending_topics: list[TrendingTopic]