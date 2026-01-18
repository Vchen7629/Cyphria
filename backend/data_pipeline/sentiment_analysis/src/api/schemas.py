from pydantic import BaseModel
from datetime import datetime

class UnprocessedComment(BaseModel):
    comment_id: str
    comment_body: str
    category: str
    detected_products: list[str]
    created_utc: datetime

class ProductSentiment(BaseModel):
    comment_id: str
    product_name: str
    category: str
    sentiment_score: float
    created_utc: datetime

class SentimentResult(BaseModel):
    """Result of a sentiment analysis airflow run"""
    comments_inserted: int
    comments_updated: int
    cancelled: bool = False

class RunRequest(BaseModel):
    """Request containing the category polling interval to the /run endpoint"""
    category: str

class RunResponse(BaseModel):
    """Response from /run endpoint"""
    status: str # "completed" | "cancelled" | "error"
    result: SentimentResult | None = None
    error: str | None = None

class HealthResponse(BaseModel):
    """Response from /health endpoint"""
    status: str # "healthy" | "unhealthy"
    db_connected: bool