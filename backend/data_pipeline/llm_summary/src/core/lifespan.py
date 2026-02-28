from typing import Any
from typing import AsyncGenerator
from openai import OpenAI
from fastapi import FastAPI
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from data_pipeline_utils.job_state_manager import JobState
from src.api.schemas import CurrentJob
from shared_core.logger import StructuredLogger
from shared_db.conn import create_verified_connection_pool
from src.core.settings_config import Settings

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Managed api lifecycle, resources created once at startup and cleanup up on shutdown"""
    logger = StructuredLogger(pod="llm_summary")
    logger.info(event_type="llm_summary startup", message="Initializing llm summary service")

    db_pool = create_verified_connection_pool(
        settings.DB_HOST,
        settings.DB_PORT,
        settings.DB_NAME,
        settings.DB_USER,
        settings.DB_PASS,
        logger,
        service_name="llm_summary",
    )

    executor: ThreadPoolExecutor = ThreadPoolExecutor(
        max_workers=1, thread_name_prefix="summary_service"
    )

    # Store these values in app state for dependency injection
    app.state.db_pool = db_pool
    app.state.logger = logger
    app.state.llm_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    app.state.job_state = JobState[CurrentJob]()
    app.state.llm_model_name = settings.LLM_MODEL
    app.state.executor = executor

    logger.info(event_type="llm_summary startup", message="Summary service ready")

    yield

    logger.info(event_type="llm_summary shutdown", message="Shutting down llm summary service...")
    db_pool.close()
    logger.info(event_type="llm_summary shutdown", message="DB pool closed")
    executor.shutdown(wait=True)
    logger.info(event_type="llm_summary shutdown", message="executor shutdown")
    logger.info(event_type="llm_summary shutdown", message="Shutdown complete")
