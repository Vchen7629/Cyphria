from typing import Any
from typing import AsyncGenerator
from fastapi import FastAPI
from httpx import AsyncClient
from httpx import ASGITransport
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.db_utils.pg_conn import get_session
from src.core.logger import StructuredLogger
from tests.types.fastapi import FastAPITestClient
from src.routes.home import routes as home_router
from src.routes.topic import routes as topic_router
from src.routes.products import routes as product_router
from src.routes.category import routes as category_router
import pytest_asyncio
import pytest

@asynccontextmanager
async def null_lifespan(_app: FastAPI) -> AsyncGenerator[Any, Any]:
    """No-op lifespan for testing - state is set by fixtures"""
    yield

@pytest_asyncio.fixture
async def fastapi_client(
    test_async_session: async_sessionmaker[AsyncSession],
    clean_tables: None
) -> AsyncGenerator[FastAPITestClient, None]:
    """FastAPI AsyncClient with test database session."""

    test_app = FastAPI(lifespan=null_lifespan)
    test_app.include_router(home_router)
    test_app.include_router(topic_router)
    test_app.include_router(category_router)
    test_app.include_router(product_router)

    test_app.state.async_session = test_async_session
    test_app.state.logger = StructuredLogger(pod="insights_api_test")

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with test_async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    test_app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        yield FastAPITestClient(client=client, app=test_app)

@pytest.fixture(scope="function")
def mock_fastapi() -> FastAPI:
    """mock fastapi client for unit testing."""

    test_app = FastAPI()
    test_app.include_router(home_router)
    test_app.include_router(topic_router)
    test_app.include_router(category_router)
    test_app.include_router(product_router)

    test_app.state.logger = StructuredLogger(pod="insights_api_test")

    return test_app