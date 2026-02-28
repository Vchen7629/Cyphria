from tests.fixtures.service import null_lifespan
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Any
from typing import Generator
from shared_core.logger import StructuredLogger
from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from src.api.routes import router as base_router
from src.api.schemas import CurrentJob
from data_pipeline_utils.job_state_manager import JobState
from tests.types.fastapi import FastAPITestClient
import pytest


@pytest.fixture
def fastapi_client(db_pool: ConnectionPool) -> Generator[FastAPITestClient, None, None]:
    """Fastapi TestClient with mocked heavy dependencies for integration tests"""
    test_app = FastAPI(lifespan=null_lifespan)
    test_app.include_router(base_router)

    # Mock executor that runs tasks synchronously and returns a completed Future
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

    test_app.state.db_pool = db_pool
    test_app.state.executor = mock_executor
    test_app.state.logger = StructuredLogger(pod="ranking_service")
    test_app.state.job_state = JobState[CurrentJob]()

    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield FastAPITestClient(client=client, app=test_app)


@pytest.fixture(scope="session")
def mock_fastapi() -> FastAPI:
    """Mock fastapi to be used for unit tests"""
    app = FastAPI()
    app.include_router(base_router)

    return app
