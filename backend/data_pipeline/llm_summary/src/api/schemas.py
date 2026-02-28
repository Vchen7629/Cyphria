from pipeline_types.data_pipeline import JobStatus
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class SummaryResult(BaseModel):
    """Result of a summary airflow run"""

    products_summarized: int
    cancelled: bool = False


class CurrentJob(BaseModel):
    """Currently running job state"""

    status: JobStatus
    time_window: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[SummaryResult] = None
    error: Optional[str] = None


class RunRequest(BaseModel):
    """Request body to the /run endpoint"""

    time_window: str


class RunResponse(BaseModel):
    """Response from /run endpoint"""

    status: str  # "started"


class HealthResponse(BaseModel):
    """Response from /health endpoint"""

    status: str  # "healthy" | "unhealthy"
    db_connected: bool
