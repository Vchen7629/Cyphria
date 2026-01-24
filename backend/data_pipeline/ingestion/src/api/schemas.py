from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

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

class CurrentJob(BaseModel):
    """Currently running job state"""
    status: JobStatus # "pending" | "running" | "completed" | "failed" | "cancelled"
    product_topic: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[IngestionResult] = None
    error: Optional[str] = None

class RunRequest(BaseModel):
    """Request to the /run endpoint"""
    product_topic: str          # Product topic like "GPU" or "Laptop"
    subreddits: list[str]       # list of subreddits for that category

class RunResponse(BaseModel):
    """Response from /run endpoint"""
    status: str # "started"

class HealthResponse(BaseModel):
    """Response from /health endpoint"""
    status: str # "healthy" | "unhealthy"
    db_connected: bool
    reddit_connected: bool