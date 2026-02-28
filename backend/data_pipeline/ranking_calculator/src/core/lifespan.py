from typing import Any
from typing import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from shared_core.logger import StructuredLogger
from shared_db.conn import create_verified_connection_pool
from data_pipeline_utils.job_state_manager import JobState
from src.api.schemas import CurrentJob
from src.core.settings_config import Settings

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """
    Managed api lifecycle, resources created once
    at startup and cleanup up on shutdown
    """
    logger = StructuredLogger(pod="ranking_service")
    logger.info(event_type="ranking_service startup", message="Initializing ranking service")

    db_pool = create_verified_connection_pool(
        settings.DB_HOST,
        settings.DB_PORT,
        settings.DB_NAME,
        settings.DB_USER,
        settings.DB_PASS,
        logger,
        service_name="ranking_service",
    )

    # Check database health before proceeding, exit if database non responsive
    try:
        with db_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            logger.info(
                event_type="ranking_service startup", message="Database health check passed"
            )
    except Exception as e:
        logger.error(
            event_type="ranking_service startup", message=f"Database health check failed: {e}"
        )
        db_pool.close()
        raise

    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ranking_service")

    # Store these values in app state for dependency injection
    app.state.db_pool = db_pool
    app.state.logger = logger
    app.state.executor = executor
    app.state.job_state = JobState[CurrentJob]()

    logger.info(event_type="ranking_service startup", message="Ranking service ready")

    yield

    logger.info(event_type="ranking_service shutdown", message="Shutting down ranking service")
    db_pool.close()
    logger.info(event_type="ranking_service shutdown", message="Database connection pool closed")
    executor.shutdown(wait=True, cancel_futures=False)
    logger.info(event_type="ranking_service shutdown", message="Executor closed")
    logger.info(event_type="ranking_service shutdown", message="Shutdown complete")
