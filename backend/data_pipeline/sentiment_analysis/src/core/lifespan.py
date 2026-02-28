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
from src.core.model import sentiment_analysis_model
from src.preprocessing.sentiment_analysis import Aspect_Based_Sentiment_Analysis

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """
    Managed api lifecycle, resources created once
    at startup and cleanup up on shutdown
    """
    logger = StructuredLogger(pod="sentiment_analysis")
    logger.info(
        event_type="sentiment_analysis startup", message="Initializing sentiment analysis service"
    )

    db_pool = create_verified_connection_pool(
        settings.DB_HOST,
        settings.DB_PORT,
        settings.DB_NAME,
        settings.DB_USER,
        settings.DB_PASS,
        logger,
        service_name="sentiment_analysis",
    )

    logger.info(event_type="sentiment_analysis startup", message="loading ABSA model")
    absa_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="absa_inference")
    model_data = sentiment_analysis_model("yangheng/deberta-v3-base-absa-v1.1")
    tokenizer, model = model_data
    absa_model = Aspect_Based_Sentiment_Analysis(
        tokenizer,
        model,
        absa_executor,
        model_batch_size=settings.SENTIMENT_BATCH_SIZE,
        logger=logger,
    )

    processing_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="sentiment_analysis")

    # Store these values in app state for dependency injection
    app.state.db_pool = db_pool
    app.state.logger = logger
    app.state.model = absa_model
    app.state.executor = processing_executor
    app.state.job_state = JobState[CurrentJob]()

    logger.info(event_type="sentiment_analysis startup", message="Sentiment analysis service ready")

    yield

    logger.info(
        event_type="sentiment_analysis shutdown",
        message="Shutting down sentiment analysis service...",
    )
    logger.info(event_type="sentiment_analysis shutdown", message="Closing db pool...")
    db_pool.close()
    logger.info(event_type="sentiment_analysis shutdown", message="DB pool closed...")
    logger.info(event_type="sentiment_analysis shutdown", message="Shutting down executors...")
    absa_executor.shutdown(wait=True)
    processing_executor.shutdown(wait=True)
    logger.info(event_type="sentiment_analysis shutdown", message="Executor shutdown")
    logger.info(event_type="sentiment_analysis shutdown", message="Shutdown complete")
