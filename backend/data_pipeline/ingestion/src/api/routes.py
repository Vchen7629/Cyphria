from typing import Optional
from fastapi import Request
from fastapi import APIRouter
from fastapi import HTTPException
from concurrent.futures import ThreadPoolExecutor
from src.api.job_state import JobState
from src.api.schemas import HealthResponse
from src.api.schemas import RunResponse
from src.api.schemas import RunRequest
from src.api.schemas import CurrentJob
from src.utils.validation import validate_list
from src.utils.validation import validate_string
from src.ingestion_service import IngestionService
from src.product_detector.base import BuildDetectorRegex
from src.product_detector.base import ProductDetector
import asyncio

router = APIRouter()

# global job state thats initialized in lifespan
job_state: JobState | None = None


@router.post("/run", response_model=RunResponse)
async def trigger_ingestion(request: Request, body: RunRequest) -> RunResponse:
    """
    Trigger an ingestion run asynchronously

    Returns:
        RunResponse with job_id and status="started"

    Raises:
        HTTPException if no category or job state
    """
    # lock to prevent duplicate calls to this endpoint from retriggering ingestion
    category: str = body.category
    topic_list: list[str] = body.topic_list
    subreddit_list: list[str] = body.subreddit_list

    validate_string(category, "category", raise_http=True)
    validate_list(topic_list, "topic_list", raise_http=True)
    validate_list(subreddit_list, "subreddit_list", raise_http=True)

    if not job_state:
        raise HTTPException(status_code=400, detail="Missing job_state, cant trigger run")

    if job_state.is_running():
        raise HTTPException(status_code=409, detail="Ingestion already in progress")

    job_state.create_job(body.category, subreddit_list)

    # Build detectors for the requested topics
    logger = request.app.state.logger
    regex_builder = BuildDetectorRegex()
    detector_patterns = regex_builder.process_all_topics(topic_list, logger=logger)

    detectors: dict[str, Optional[ProductDetector]] = {}
    for topic, pattern in zip(topic_list, detector_patterns):
        if pattern:
            mapping = regex_builder.get_mapping_for_topic(topic)
            if mapping:
                detectors[topic.upper().strip()] = ProductDetector(pattern=pattern, mapping=mapping)
            else:
                detectors[topic.upper().strip()] = None
        else:
            detectors[topic.upper().strip()] = None

    service = IngestionService(
        reddit_client=request.app.state.reddit_client,
        db_pool=request.app.state.db_pool,
        logger=logger,
        topic_list=topic_list,
        subreddit_list=subreddit_list,
        normalizer=request.app.state.normalizer,
        detectors=detectors,
        fetch_executor=request.app.state.fetch_reddit_posts_executor,
    )

    executor: ThreadPoolExecutor = request.app.state.main_processing_executor
    loop = asyncio.get_event_loop()

    # run worker in thread pool to prevent blocking the polling /status endpoint
    loop.run_in_executor(executor, service.run_single_cycle, job_state)

    return RunResponse(status="started")


@router.get("/status", response_model=CurrentJob)
async def get_job_status() -> CurrentJob:
    """
    Get status of a ingestion job
    Airflow HttpSensor polls this endpoint until status is 'completed' or 'failed'

    Raises:
        HTTPException if no job state
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
