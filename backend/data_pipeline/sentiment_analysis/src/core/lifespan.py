from src.db_utils.conn import create_connection_pool
from src.core.logger import StructuredLogger
from src.core.settings_config import Settings
from src.core.model import sentiment_analysis_model
from src.preprocessing.sentiment_analysis import Aspect_Based_Sentiment_Analysis
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """
    Managed api lifecycle, resources created once
    at startup and cleanup up on shutdown
    """
    logger = StructuredLogger(pod="sentiment_analysis")
    logger.info(event_type="sentiment_analysis startup", message="Initializing sentiment analysis service")

    logger.info(event_type="sentiment_analysis startup", message="Creating database connection pool")
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

    logger.info(event_type="sentiment_analysis startup", message="loading ABSA model")
    executor = ThreadPoolExecutor(max_workers=1)
    model_data = sentiment_analysis_model("yangheng/deberta-v3-base-absa-v1.1")
    tokenizer, model = model_data
    absa_model = Aspect_Based_Sentiment_Analysis(tokenizer, model, executor, model_batch_size=settings.SENTIMENT_BATCH_SIZE)

    # Store these values in app state for dependency injection
    app.state.db_pool = db_pool
    app.state.logger = logger
    app.state.model = absa_model

    yield

    logger.info(event_type="sentiment_analysis shutdown", message="Shutting down sentiment analysis service...")
    logger.info(event_type="sentiment_analysis shutdown", message="Closing db pool...")
    db_pool.close()
    logger.info(event_type="sentiment_analysis shutdown", message="DB pool closed...")
    logger.info(event_type="sentiment_analysis shutdown", message="Shutting down executor...")
    executor.shutdown(wait=True)
    logger.info(event_type="sentiment_analysis shutdown", message="Executor shutdown")
    logger.info(event_type="sentiment_analysis shutdown", message="Shutdown complete")
