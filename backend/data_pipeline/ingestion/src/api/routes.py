from src.api.schemas import HealthResponse
from fastapi.routing import APIRouter
from src.api.schemas import RunResponse
from src.worker import IngestionService
from fastapi import Request, HTTPException
from src.api.signal_handler import run_state

router = APIRouter(prefix="/worker", tags=["routes"])

@router.post("/run", response_model=RunResponse)
def trigger_ingestion(request: Request) -> RunResponse:
    """
    Trigger an ingestion run.

    This endpoint blocks until ingestion completes. For hourly scheduled runs,
    Airflow should call this endpoint and wait for the response.

    On SIGTERM/SIGINT, the running service will be gracefully cancelled
    and remaining data will be saved before returning.

    Returns:
        RunResponse containing the status and various metrics
    """
    # lock to prevent duplicate calls to this endpoint from retriggering ingestion
    if run_state.run_in_progress:
        raise HTTPException(
            status_code=409,
            detail="Ingestion already in progress"
        )

    run_state.run_in_progress = True

    try:
        # Create service with injected dependencies
        service = IngestionService(
            reddit_client=request.app.state.reddit_client,
            db_pool=request.app.state.db_pool,
            logger=request.app.state.logger,
            category=request.app.state.category,
            subreddits=request.app.state.subreddits,
            detector=request.app.state.detector,
            normalizer=request.app.state.normalizer,
        )

        # Store reference so signal handler can request cancellation
        run_state.current_service = service

        result = service.run()

        return RunResponse(
            status="cancelled" if result.cancelled else "completed",
            result=result,
        )
    except Exception as e:
        request.app.state.logger.error(
            event_type="ingestion",
            message=f"Ingestion failed: {e}"
        )
        return RunResponse(
            status="error",
            error=str(e),
        )
    finally:
        run_state.current_service = None
        run_state.run_in_progress = False


@router.get("/health", response_model=HealthResponse)
def health_check(request: Request) -> HealthResponse:
    """
    Health check endpoint for Kubernetes probes.

    Checks database connectivity and Reddit client status.
    """
    db_ok = False
    reddit_ok = False

    # Check database
    try:
        with request.app.state.db_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        db_ok = True
    except Exception:
        pass

    # Check Reddit client (verify authentication)
    try:
        # This makes a lightweight API call to verify credentials
        _ = request.app.state.reddit_client.user.me()
        reddit_ok = True
    except Exception:
        pass

    status = "healthy" if (db_ok and reddit_ok) else "unhealthy"

    return HealthResponse(
        status=status,
        db_connected=db_ok,
        reddit_connected=reddit_ok,
    )


@router.get("/ready")
def readiness_check() -> dict[str, bool]:
    """
    Readiness probe - returns 200 when service is ready to accept requests.
    """
    return {"ready": True}