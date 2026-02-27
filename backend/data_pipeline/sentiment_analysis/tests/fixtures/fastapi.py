from typing import Any
from typing import Generator
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
from contextlib import asynccontextmanager
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from shared_core.logger import StructuredLogger
from src.api import routes
from src.api.job_state import JobState
from src.api.routes import router as base_router
from tests.types.fastapi import FastAPITestClient
import pytest


@asynccontextmanager
async def null_lifespan(_app: FastAPI) -> Any:
    """No-op lifespan for testing - state is set by fixtures"""
    yield


@pytest.fixture
def fastapi_client(
    db_pool: ConnectionPool, mock_absa: MagicMock
) -> Generator[FastAPITestClient, None, None]:
    """Fastapi TestClient with mocked heavy dependencies"""
    test_app = FastAPI(lifespan=null_lifespan)
    test_app.include_router(base_router)
    mock_executor = MagicMock(spec=ThreadPoolExecutor)

    def mock_submit(fn: Any, *args: Any) -> Any:
        """Execute function synchronously and return a completed Future"""
        future = Future()
        try:
            result = fn(*args)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
        return future

    mock_executor.submit = mock_submit

    job_state_instance = JobState()

    test_app.state.db_pool = db_pool
    test_app.state.logger = StructuredLogger(pod="sentiment_service_test")
    test_app.state.model = mock_absa
    test_app.state.executor = mock_executor

    routes.job_state = job_state_instance

    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield FastAPITestClient(client=client, app=test_app)


@pytest.fixture(scope="session")
def mock_fastapi() -> FastAPI:
    """Mock fastapi to be used for unit tests"""
    app = FastAPI()
    app.include_router(base_router)

    return app
