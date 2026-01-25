from fastapi import Request
from fastapi import APIRouter
from fastapi import HTTPException
from concurrent.futures import ThreadPoolExecutor
from src.sentiment_service import SentimentService
from src.api.job_state import JobState
from src.api.schemas import CurrentJob
from src.api.schemas import RunRequest
from src.api.schemas import RunResponse
from src.api.schemas import HealthResponse
from src.api.signal_handler import run_state
import asyncio

router = APIRouter()

# global job state thats initialized in lifespan
job_state: JobState | None = None

@router.post("/run", response_model=RunResponse)
async def trigger_sentiment_analysis(request: Request, body: RunRequest) -> RunResponse: 
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
        raise HTTPException(
            status_code=409,
            detail="Ranking already in progress"
        )
    
    if job_state:
        job_state.create_job(product_topic)

    service = SentimentService(
        logger = request.app.state.logger,
        category = product_topic,
        db_pool = request.app.state.db_pool,
        model = request.app.state.model
    )

    run_state.current_service = service
    run_state.run_in_progress = True

    executor: ThreadPoolExecutor = request.app.state.executor
    loop = asyncio.get_event_loop()

    if job_state:
        loop.run_in_executor(executor, service.run_single_cycle, job_state)

    return RunResponse(status="started")

@router.get("/status", response_model=CurrentJob)
async def get_job_status() -> CurrentJob:
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