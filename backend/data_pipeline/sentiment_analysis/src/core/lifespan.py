from typing import Any
from typing import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from shared_core.logger import StructuredLogger
from shared_db.conn import create_connection_pool
from src.api import routes
from src.api.job_state import JobState
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

    logger.info(
        event_type="sentiment_analysis startup", message="Creating database connection pool"
    )
    db_pool = create_connection_pool(
        settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASS
    )

    # Check database health before proceeding, exit if database non responsive
    try:
        with db_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            logger.info(event_type="data_ingestion startup", message="Database health check passed")
    except Exception as e:
        logger.error(
            event_type="data_ingestion startup", message=f"Database health check failed: {e}"
        )
        db_pool.close()
        raise

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
    job_state_instance = JobState()

    # Store these values in app state for dependency injection
    app.state.db_pool = db_pool
    app.state.logger = logger
    app.state.model = absa_model
    app.state.executor = processing_executor

    routes.job_state = job_state_instance

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
