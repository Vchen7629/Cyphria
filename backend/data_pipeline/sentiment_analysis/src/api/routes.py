from src.api.schemas import HealthResponse
from src.api.schemas import RunResponse
from src.api.schemas import RunRequest
from src.api.signal_handler import run_state
from src.worker import StartService
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

@router.post("/run", response_model=RunResponse)
def trigger_sentiment_analysis(request: Request, body: RunRequest) -> RunResponse: 
    """
    Trigger an sentiment analysis run.

    This endpoint blocks until sentiment analysis completes. For hourly scheduled runs,
    Airflow should call this endpoint and wait for the response.

    On SIGTERM/SIGINT, the running service will be gracefully cancelled
    and remaining data will be saved before returning.

    Returns:
        RunResponse containing the status and various metrics
    """
    # lock to prevent duplicate calls to this endpoint from 
    # retriggering the sentiment analysis job
    if run_state.run_in_progress:
        raise HTTPException(
            status_code=409,
            detail="Ingestion already in progress"
        )

    run_state.run_in_progress = True

    try:
        service = StartService(
            logger = request.app.state.logger,
            category = body.category,
            db_pool = request.app.state.db_pool,
            model = request.app.state.model
        )

        run_state.current_service = service

        result = service.run()

        return RunResponse(
            status="cancelled" if result.cancelled else "completed",
            result=result
        )
    except Exception as e:
        request.app.state.logger.error(
            event_type="ingestion",
            message=f"Ingestion failed: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    finally:
        run_state.current_service = None
        run_state.run_in_progress = False

@router.get("/health", response_model=HealthResponse)
def health_check(request: Request) -> HealthResponse:
    """ Health check endpoint for Kubernetes probes, Checks database connectivity"""
    db_ok = False

    # Check database
    try:
        with request.app.state.db_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        db_ok = True
    except Exception:
        pass

    return HealthResponse(
        status="healthy" if db_ok else "unhealthy",
        db_connected=db_ok
    )

@router.get("/ready")
def readiness_check() -> dict[str, bool]:
    """
    Readiness probe - returns 200 when service is ready to accept requests.
    """
    return {"ready": True}