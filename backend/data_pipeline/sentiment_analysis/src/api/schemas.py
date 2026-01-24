from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class JobStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CurrentJob(BaseModel):
    """Currently running job state"""
    status: JobStatus # "pending" | "running" | "completed" | "failed" | "cancelled"
    category: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[SentimentResult] = None
    error: Optional[str] = None

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
    status: str # "started"

class HealthResponse(BaseModel):
    """Response from /health endpoint"""
    status: str # "healthy" | "unhealthy"
    db_connected: bool