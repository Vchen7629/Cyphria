from src.core.settings import Settings
from src.core.logger import StructuredLogger
from src.db_utils.conn import engine
from src.db_utils.conn import async_session
from typing import AsyncGenerator
from typing import Any
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Managed api lifecycle, resources created once at startup and cleanup up on shutdown"""
    logger = StructuredLogger(pod="insights_api")
    logger.info(event_type="insights_api startup", message="Initializing insights api")

    # Check database health before proceeding, exit if database non responsive 
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        
        logger.info(event_type="insights_api startup", message="Database health check passed")
    except Exception as e:
        logger.error(event_type="insights_api startup", message=f"Database health check failed: {e}")
        await engine.dispose()
        raise

    # Store these values in app state for dependency injection
    app.state.async_session = async_session
    app.state.logger = logger
    logger.info(event_type="insights_api startup", message="Insights API ready")

    yield

    logger.info(event_type="insights_api shutdown", message="Shutting down insights api")
    await engine.dispose()
    logger.info(event_type="insights_api shutdown", message="Database connection pool closed")
    logger.info(event_type="insights_api shutdown", message="Shutdown complete")