from fastapi import Depends
from fastapi import APIRouter
from fastapi import Request
from fastapi import HTTPException
from datetime import datetime
from datetime import timezone
from concurrent.futures import ThreadPoolExecutor
from pipeline_types.data_pipeline import JobStatus
from data_pipeline_utils.job_state_manager import JobState
from src.api.schemas import CurrentJob
from src.api.schemas import RunRequest
from src.api.schemas import RunResponse
from src.api.schemas import HealthResponse
from src.summary_service import LLMSummaryService
import asyncio

router = APIRouter()


def get_job_state(request: Request) -> JobState[CurrentJob]:
    return request.app.state.job_state


@router.post("/run", response_model=RunResponse)
async def trigger_llm_summarization(
    request: Request, body: RunRequest, job_state: JobState[CurrentJob] = Depends(get_job_state)
) -> RunResponse:
    """
    Trigger an summary run asynchronously

    Returns:
        RunResponse with job_id and status="started"

    Raises:
        HttpException if no time_window or job_state
    """
    time_window = body.time_window
    if not time_window or time_window.strip() == "":
        raise HTTPException(status_code=400, detail="Missing time_window in your request")

    if not job_state:
        raise HTTPException(status_code=400, detail="Missing job_state, cant trigger run")

    # lock to prevent duplicate calls to this endpoint from retriggering ranking
    if job_state.is_running():
        raise HTTPException(status_code=409, detail="Summary already in progress")

    job_state.set_running_job(
        CurrentJob(
            time_window=time_window,
            status=JobStatus.RUNNING,
            started_at=datetime.now(tz=timezone.utc),
        )
    )

    service = LLMSummaryService(
        llm_model_name=request.app.state.llm_model_name,
        llm_client=request.app.state.llm_client,
        time_window=body.time_window,
        logger=request.app.state.logger,
        db_pool=request.app.state.db_pool,
    )

    executor: ThreadPoolExecutor = request.app.state.executor
    loop = asyncio.get_event_loop()

    loop.run_in_executor(executor, service.run_single_cycle, job_state)

    return RunResponse(status="started")


@router.get("/status", response_model=CurrentJob)
async def get_job_status(job_state: JobState[CurrentJob] = Depends(get_job_state)) -> CurrentJob:
    """
    Get status of a summary job
    Airflow HttpSensor polls this endpoint until status is 'completed' or 'failed'

    Args:
        job_state: current job state

    Raises:
        HTTPException if no job_state
    """
    if not job_state:
        raise HTTPException(status_code=400, detail="Missing job_state, cant check status")

    job = job_state.get_current_job()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/health", response_model=HealthResponse)
def health_check(request: Request) -> HealthResponse:
    """Health check endpoint for Kubernetes probes, Checks database connectivity"""
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

    return HealthResponse(status="healthy" if db_ok else "unhealthy", db_connected=db_ok)


@router.get("/ready")
def readiness_check() -> dict[str, bool]:
    """
    Readiness probe - returns 200 when service is ready to accept requests.
    """
    return {"ready": True}
