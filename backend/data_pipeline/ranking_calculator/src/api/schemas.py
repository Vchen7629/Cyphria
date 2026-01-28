from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RankingResult(BaseModel):
    """Result of a ranking airflow run"""

    products_processed: int
    cancelled: bool = False


class CurrentJob(BaseModel):
    """Currently running job state"""

    status: JobStatus  # "pending" | "running" | "completed" | "failed" | "cancelled"
    product_topic: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[RankingResult] = None
    error: Optional[str] = None


class SentimentAggregate(BaseModel):
    """Aggregated sentiment data for a single product from product_sentiment table."""

    product_name: str
    avg_sentiment: float
    mention_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    approval_percentage: int


class ProductScore(BaseModel):
    """Data model for product score row to be inserted into gold layer."""

    product_name: str
    product_topic: str
    time_window: str  # "90d" or "all_time"

    # Ranking
    rank: int
    grade: str  # "S", "A+", "A", "A-", "B+", etc.

    # Scores
    bayesian_score: float
    avg_sentiment: float
    approval_percentage: int

    # Metrics
    mention_count: int
    positive_count: int
    negative_count: int
    neutral_count: int

    # Badges
    is_top_pick: bool = False
    is_most_discussed: bool = False
    has_limited_data: bool = False

    # Metadata
    calculation_date: datetime


class RunRequest(BaseModel):
    """Request to the /run endpoint"""

    product_topic: str  # product_topic like "GPU" or "Laptop"
    time_window: str  # either "90d" or "all_time"


class RunResponse(BaseModel):
    """Response from /run endpoint"""

    status: str  # "started"


class HealthResponse(BaseModel):
    """Response from /health endpoint"""

    status: str  # "healthy" | "unhealthy"
    db_connected: bool
