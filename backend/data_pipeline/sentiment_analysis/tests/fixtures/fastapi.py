from typing import Any
from typing import Generator
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
from contextlib import asynccontextmanager
from src.core.logger import StructuredLogger
from src.api.routes import router as base_router
from tests.types.fastapi import FastAPITestClient
import pytest

@asynccontextmanager
async def null_lifespan(_app: FastAPI) -> Any:
    """No-op lifespan for testing - state is set by fixtures"""
    yield

@pytest.fixture
def fastapi_client(db_pool: ConnectionPool, mock_absa: MagicMock) -> Generator[FastAPITestClient, None, None]:
    """Fastapi TestClient with mocked heavy dependencies"""
    test_app = FastAPI(lifespan=null_lifespan)
    test_app.include_router(base_router)

    test_app.state.db_pool = db_pool
    test_app.state.logger = StructuredLogger(pod="ingestion_service_test")
    test_app.state.model = mock_absa

    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield FastAPITestClient(client=client, app=test_app)

@pytest.fixture(scope="session")
def mock_fastapi() -> FastAPI:
    """Mock fastapi to be used for unit tests"""
    app = FastAPI()
    app.include_router(base_router)

    return app