from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Any
from typing import Generator
from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from src.api import routes
from src.api.job_state import JobState
from src.api.routes import router as base_router
from src.core.logger import StructuredLogger
from tests.utils.service import null_lifespan
from tests.utils.classes import FastAPITestClient
from src.products.detector_factory import DetectorFactory
from src.products.normalizer_factory import NormalizerFactory
import pytest


@pytest.fixture
def fastapi_client(
    db_pool: ConnectionPool, mock_reddit_client: MagicMock
) -> Generator[FastAPITestClient, None, None]:
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
    job_state_instance = JobState()

    test_app.state.db_pool = db_pool
    test_app.state.reddit_client = mock_reddit_client
    test_app.state.logger = StructuredLogger(pod="ingestion_service_test")
    test_app.state.detector = DetectorFactory.get_detector("GPU")
    test_app.state.normalizer = NormalizerFactory
    test_app.state.executor = mock_executor
    test_app.state.fetch_reddit_posts_executor = mock_executor
    test_app.state.main_processing_executor = mock_executor

    routes.job_state = job_state_instance

    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield FastAPITestClient(client=client, app=test_app)


@pytest.fixture(scope="session")
def mock_fastapi() -> FastAPI:
    """Mock fastapi to be used for unit tests"""
    app = FastAPI()
    app.include_router(base_router)

    return app
