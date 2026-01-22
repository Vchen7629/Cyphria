from src.db.conn import create_connection_pool
from src.core.logger import StructuredLogger
from src.core.settings_config import Settings
from typing import Any
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from openai import OpenAI

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
    
    llm_model_name = settings.LLM_MODEL
    llm_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Store these values in app state for dependency injection
    app.state.db_pool = db_pool
    app.state.logger = logger
    app.state.llm_client = llm_client
    app.state.llm_model_name = llm_model_name

    yield

    logger.info(event_type="llm_summary shutdown", message="Shutting down llm summary service...")
    logger.info(event_type="llm_summary shutdown", message="Closing db pool...")
    db_pool.close()
    logger.info(event_type="llm_summary shutdown", message="DB pool closed...")
    logger.info(event_type="llm_summary shutdown", message="Shutdown complete")
