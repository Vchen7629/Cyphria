from typing import Any
from typing import AsyncGenerator
from openai import OpenAI
from fastapi import FastAPI
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from src.api import routes
from src.api.job_state import JobState
from src.core.logger import StructuredLogger
from src.core.settings_config import Settings
from src.db.conn import create_connection_pool

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Managed api lifecycle, resources created once at startup and cleanup up on shutdown"""
    logger = StructuredLogger(pod="llm_summary")
    logger.info(event_type="llm_summary startup", message="Initializing llm summary service")

    logger.info(event_type="llm_summary startup", message="Creating database connection pool")
    db_pool = create_connection_pool()

    # Check database health before proceeding, exit if database non responsive
    try:
        with db_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            logger.info(event_type="llm_summary startup", message="Database health check passed")
    except Exception as e:
        logger.error(event_type="llm_summary startup", message=f"Database health check failed: {e}")
        db_pool.close()
        raise

    executor: ThreadPoolExecutor = ThreadPoolExecutor(
        max_workers=1, thread_name_prefix="summary_service"
    )
    job_state_instance = JobState()

    llm_model_name = settings.LLM_MODEL
    llm_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Store these values in app state for dependency injection
    app.state.db_pool = db_pool
    app.state.logger = logger
    app.state.llm_client = llm_client
    app.state.llm_model_name = llm_model_name
    app.state.executor = executor

    routes.job_state = job_state_instance

    logger.info(event_type="llm_summary startup", message="Summary service ready")

    yield

    logger.info(event_type="llm_summary shutdown", message="Shutting down llm summary service...")
    db_pool.close()
    logger.info(event_type="llm_summary shutdown", message="DB pool closed")
    executor.shutdown(wait=True)
    logger.info(event_type="llm_summary shutdown", message="executor shutdown")
    logger.info(event_type="llm_summary shutdown", message="Shutdown complete")
