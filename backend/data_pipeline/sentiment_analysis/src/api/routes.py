from data_pipeline_utils.run_single_cycle import run_single_cycle
from fastapi import Depends
from fastapi import Request
from fastapi import APIRouter
from fastapi import HTTPException
from datetime import datetime
from datetime import timezone
from concurrent.futures import ThreadPoolExecutor
from pipeline_types.data_pipeline import JobStatus
from data_pipeline_utils.job_state_manager import JobState
from src.sentiment_service import SentimentService
from src.api.schemas import CurrentJob
from src.api.schemas import RunRequest
from src.api.schemas import RunResponse
from src.api.schemas import HealthResponse
import asyncio

router = APIRouter()


def get_job_state(request: Request) -> JobState[CurrentJob]:
    return request.app.state.job_state


@router.post("/run", response_model=RunResponse)
async def trigger_sentiment_analysis(
    request: Request, body: RunRequest, job_state: JobState[CurrentJob] = Depends(get_job_state)
) -> RunResponse:
    """
    Trigger an sentiment analysis run asynchronously

    Returns:
        RunResponse with status="started"

    Raises:
        HTTPException if category is missing or none
    """
    product_topic: str = body.product_topic
    if not product_topic or product_topic.strip == "":
        raise HTTPException(status_code=400, detail="Missing product_topic parameter")

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

    service = SentimentService(
        logger=request.app.state.logger,
        product_topic=product_topic,
        db_pool=request.app.state.db_pool,
        model=request.app.state.model,
    )

    executor: ThreadPoolExecutor = request.app.state.executor
    loop = asyncio.get_event_loop()

    loop.run_in_executor(
        executor,
        run_single_cycle,
        job_state,
        "sentiment_service",
        service.run_sentiment_pipeline,
        request.app.state.logger,
    )

    return RunResponse(status="started")


@router.get("/status", response_model=CurrentJob)
async def get_job_status(job_state: JobState[CurrentJob] = Depends(get_job_state)) -> CurrentJob:
    """
    Get status of a ingestion job
    Airflow HttpSensor polls this endpoint until status is 'completed' or 'failed'

    Returns:
        the current job

    Raises:
        HTTPException is job_state is none
    """
    if not job_state:
        raise HTTPException(status_code=400, detail="Missing job_state, cant fetch status")

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
