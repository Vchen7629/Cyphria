from src.api.job_state import JobState
from concurrent.futures import ThreadPoolExecutor
from src.product_utils.normalizer_factory import NormalizerFactory
from src.core.settings_config import Settings
from src.core.reddit_client_instance import createRedditClient
from src.db_utils.conn import create_connection_pool
from src.core.logger import StructuredLogger
from src.api import routes
from typing import AsyncGenerator
from typing import Any
from contextlib import asynccontextmanager
from fastapi import FastAPI

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """
    Managed api lifecycle, resources created once
    at startup and cleanup up on shutdown
    """
    logger = StructuredLogger(pod="data_ingestion")
    logger.info(event_type="data_ingestion startup", message="Initializing ingestion service")

    logger.info(event_type="data_ingestion startup", message="Creating database connection pool")
    db_pool = create_connection_pool()

    # Check database health before proceeding, exit if database non responsive 
    try:
        with db_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            logger.info(event_type="data_ingestion startup", message="Database health check passed")
    except Exception as e:
        logger.error(event_type="data_ingestion startup", message=f"Database health check failed: {e}")
        db_pool.close()
        raise 
    
    logger.info(event_type="data_ingestion startup", message="Creating Reddit Client")
    reddit_client = createRedditClient()

    normalizer = NormalizerFactory

    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ingestion_service")
    
    job_state_instance = JobState()

    # Store these values in app state for dependency injection
    app.state.db_pool = db_pool
    app.state.reddit_client = reddit_client
    app.state.logger = logger
    app.state.normalizer = normalizer
    app.state.executor = executor

    routes.job_state = job_state_instance

    logger.info(event_type="data_ingestion startup", message="Ingestion service ready")

    yield

    logger.info(event_type="data_ingestion shutdown", message="Shutting down ingestion service")
    db_pool.close()
    logger.info(event_type="data_ingestion shutdown", message="Database connection pool closed")
    executor.shutdown(wait=True, cancel_futures=False)
    logger.info(event_type="data_ingestion shutdown", message="Executor closed")
    logger.info(event_type="data_ingestion shutdown", message="Shutdown complete")