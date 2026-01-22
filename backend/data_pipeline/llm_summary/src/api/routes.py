from fastapi import APIRouter
from fastapi import Request
from fastapi import HTTPException
from src.api.schemas import RunRequest
from src.api.schemas import RunResponse
from src.api.schemas import HealthResponse
from src.worker import LLMSummaryWorker
from src.api.signal_handler import run_state

router = APIRouter()

@router.post("/run", response_model=RunResponse)
def trigger_llm_summarization(request: Request, body: RunRequest) -> RunResponse:
    """
    Trigger an llm summarization run

    This endpoint blocks until llm summarization completes

    On SIGTERM/SIGINT, the running service will be gracefully cancelled
    and remaining data will be saved before returning

    Returns:
        RunResponse containing the status and amount products summarized
    """
    # lock to prevent duplicate calls to this endpoint from 
    # retriggering the sentiment analysis job
    if run_state.run_in_progress:
        raise HTTPException(
            status_code=409,
            detail="Summarization already in progress"
        )

    run_state.run_in_progress = True

    try:
        service = LLMSummaryWorker(
            llm_model_name=request.app.state.llm_model_name,
            llm_client=request.app.state.llm_client,
            time_window=body.time_window,
            logger=request.app.state.logger,
            db_pool=request.app.state.db_pool
        )

        run_state.current_service = service

        result = service.run()

        return RunResponse(
            status="cancelled" if result.cancelled else "completed",
            result=result
        )

    except Exception as e:
        request.app.state.logger.error(
            event_type="llm_summary error",
            message=f"Summarization failed: {e}"
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