from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from pipeline_types.data_pipeline import JobStatus


class SentimentResult(BaseModel):
    """Result of a sentiment analysis airflow run"""

    comments_inserted: int
    comments_updated: int


class CurrentJob(BaseModel):
    """Currently running job state"""

    status: JobStatus
    product_topic: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[SentimentResult] = None
    error: Optional[str] = None


class UnprocessedComment(BaseModel):
    comment_id: str
    comment_body: str
    product_topic: str
    detected_products: list[str]
    created_utc: datetime


class ProductSentiment(BaseModel):
    comment_id: str
    product_name: str
    product_topic: str
    sentiment_score: float
    created_utc: datetime


class RunRequest(BaseModel):
    """Request containing the product_topic polling interval to the /run endpoint"""

    product_topic: str


class RunResponse(BaseModel):
    """Response from /run endpoint"""

    status: str  # "started"


class HealthResponse(BaseModel):
    """Response from /health endpoint"""

    status: str  # "healthy" | "unhealthy"
    db_connected: bool
