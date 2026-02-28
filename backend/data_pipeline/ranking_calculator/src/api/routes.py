from shared_core.logger import StructuredLogger
from data_pipeline_utils.run_single_cycle import run_single_cycle
from datetime import timezone
from datetime import datetime
from fastapi import Depends
from fastapi import Request
from fastapi import HTTPException
from fastapi.routing import APIRouter
from concurrent.futures import ThreadPoolExecutor
from pipeline_types.data_pipeline import JobStatus
from data_pipeline_utils.job_state_manager import JobState
from src.api.schemas import HealthResponse
from src.api.schemas import RunResponse
from src.api.schemas import RunRequest
from src.api.schemas import CurrentJob
from src.ranking_service import RankingService
import asyncio

router = APIRouter()


def get_job_state(request: Request) -> JobState[CurrentJob]:
    return request.app.state.job_state


@router.post("/run", response_model=RunResponse)
async def trigger_ranking_calculation(
    request: Request, body: RunRequest, job_state: JobState[CurrentJob] = Depends(get_job_state)
) -> RunResponse:
    """
    Trigger an ranking calculation run asynchronously

    Returns:
        RunResponse with job_id and status="started"

    Raises:
        HttpException if no category/time_window/job_state
    """
    product_topic: str = body.product_topic
    time_window: str = body.time_window
    logger = StructuredLogger(pod="ranking_service")

    if not product_topic.strip() or not time_window.strip():
        raise HTTPException(
            status_code=400, detail="Missing product_topic or time_window in your request"
        )

    if not job_state:
        raise HTTPException(status_code=400, detail="Missing job_state, cant trigger run")

    # lock to prevent duplicate calls to this endpoint from retriggering ranking
    if job_state.is_running():
        raise HTTPException(status_code=409, detail="Ranking already in progress")

    job_state.set_running_job(
        CurrentJob(
            product_topic=product_topic,
            status=JobStatus.RUNNING,
            started_at=datetime.now(tz=timezone.utc),
        )
    )

    service = RankingService(
        db_pool=request.app.state.db_pool,
        logger=request.app.state.logger,
        product_topic=product_topic,
        time_window=time_window,
    )

    executor: ThreadPoolExecutor = request.app.state.executor
    loop = asyncio.get_event_loop()

    # run worker in thread pool to prevent blocking the polling /status endpoint
    loop.run_in_executor(
        executor,
        run_single_cycle,
        job_state,
        "ingestion_service",
        service.run_ranking_pipeline,
        logger,
    )

    return RunResponse(status="started")


@router.get("/status", response_model=CurrentJob)
async def get_job_status(job_state: JobState[CurrentJob] = Depends(get_job_state)) -> CurrentJob:
    """
    Get status of a ranking job
    Airflow HttpSensor polls this endpoint until status is 'completed' or 'failed'

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
    """
    Health check endpoint for Kubernetes probes.

    Checks database connectivity and Reddit client status.
    """
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

    status = "healthy" if db_ok else "unhealthy"

    return HealthResponse(status=status, db_connected=db_ok)


@router.get("/ready")
def readiness_check() -> dict[str, bool]:
    """
    Readiness probe - returns 200 when service is ready to accept requests.
    """
    return {"ready": True}
