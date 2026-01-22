from pydantic import BaseModel

class SummaryResult(BaseModel):
    """Result of a summary airflow run"""
    products_summarized: int
    cancelled: bool = False

class RunRequest(BaseModel):
    """Request body to the /run endpoint"""
    time_window: str

class RunResponse(BaseModel):
    """Response from /run endpoint"""
    status: str # "completed" | "cancelled" | "error"
    result: SummaryResult | None = None
    error: str | None = None

class HealthResponse(BaseModel):
    """Response from /health endpoint"""
    status: str # "healthy" | "unhealthy"
    db_connected: bool
