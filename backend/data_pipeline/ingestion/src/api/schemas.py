from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# Pydantic class for processed reddit comments
class ProcessedRedditComment(BaseModel):
    comment_id: str
    comment_body: str
    subreddit: str
    detected_products: list[str]
    timestamp: datetime
    score: int
    author: str
    post_id: str
    topic: str


class IngestionResult(BaseModel):
    """Result of a ingestion airflow run"""

    posts_processed: int
    comments_processed: int
    comments_inserted: int

class CurrentJob(BaseModel):
    """Currently running job state"""

    status: JobStatus
    category: str
    subreddit_list: list[str]
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[IngestionResult] = None
    error: Optional[str] = None


class RunRequest(BaseModel):
    """Request to the /run endpoint"""

    category: str  # product category like "computing" or "mobile"]
    topic_list: list[str]  # the list of product topics for this category
    subreddit_list: list[str]  # list of subreddits for this category


class RunResponse(BaseModel):
    """Response from /run endpoint"""

    status: str  # "started"


class HealthResponse(BaseModel):
    """Response from /health endpoint"""

    status: str  # "healthy" | "unhealthy"
    db_connected: bool
    reddit_connected: bool
