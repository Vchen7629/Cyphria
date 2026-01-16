from pydantic import BaseModel
from datetime import datetime

# Pydantic class for reddit comments
class RedditComment(BaseModel):
    comment_id: str
    comment_body: str
    subreddit: str
    detected_products: list[str]
    timestamp: datetime
    score: int
    author: str
    post_id: str

class IngestionResult(BaseModel):
    """Result of a ingestion airflow run"""
    posts_processed: int
    comments_processed: int
    comments_inserted: int
    cancelled: bool = False

class RunRequest(BaseModel):
    """Request to the /run endpoint"""
    category: str               # Category like "GPU" or "Laptop"
    subreddits: list[str]       # list of subreddits for that category

class RunResponse(BaseModel):
    """Response from /run endpoint"""
    status: str # "completed" | "cancelled" | "error"
    result: IngestionResult | None = None
    error: str | None = None

class HealthResponse(BaseModel):
    """Response from /health endpoint"""
    status: str # "healthy" | "unhealthy"
    db_connected: bool
    reddit_connected: bool