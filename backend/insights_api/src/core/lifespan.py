from typing import Any
from typing import AsyncGenerator
from fastapi import FastAPI
from sqlalchemy import text
from contextlib import asynccontextmanager
from src.core.settings import Settings
from src.core.logger import StructuredLogger
from src.db_utils.pg_conn import engine
from src.db_utils.pg_conn import async_session
from src.db_utils.cache_conn import cache_client

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

    # Cache (Valkey) health check, dont exit if no cache available
    cache_avail = False
    try:
        await cache_client.ping()
        cache_avail = True
        logger.info(event_type="insights_api startup", message="Valkey health check passed")
    except Exception as e:
        logger.warning(event_type="insights_api startup", message=f"Valkey health check failed: {e}")

    logger.info(event_type="insights_api startup", message="Initialized cache (valkey) client")

    # Store these values in app state for dependency injection
    app.state.async_session = async_session
    app.state.logger = logger
    app.state.cache_client = cache_client if cache_avail else None
    app.state.cache_available = cache_avail
    logger.info(event_type="insights_api startup", message="Insights API ready")

    yield

    logger.info(event_type="insights_api shutdown", message="Shutting down insights api")
    await engine.dispose()
    logger.info(event_type="insights_api shutdown", message="Database connection pool closed")

    # we should only cleanup cache if its available
    if cache_avail:
        await cache_client.close()
        cache_client.connection_pool.disconnect()
        logger.info(event_type="insights_api shutdown", message="Cache client closed")
        
    logger.info(event_type="insights_api shutdown", message="Shutdown complete")