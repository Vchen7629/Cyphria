from typing import Any
from typing import Generator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import MagicMock
from testcontainers.postgres import PostgresContainer
from psycopg_pool import ConnectionPool
import os
os.environ.setdefault("PRODUCT_CATEGORY", "GPU")
os.environ.setdefault("REDDIT_API_CLIENT_ID", "reddit_id")
os.environ.setdefault("REDDIT_API_CLIENT_SECRET", "reddit_secret")
os.environ.setdefault("REDDIT_ACCOUNT_USERNAME", "username")
os.environ.setdefault("REDDIT_ACCOUNT_PASSWORD", "password")
from src.core.logger import StructuredLogger
from src.ingestion_service import IngestionService
from src.product_utils.detector_factory import DetectorFactory
from src.product_utils.normalizer_factory import NormalizerFactory
import pytest

@asynccontextmanager
async def null_lifespan(_app: FastAPI) -> Any:
    """No-op lifespan for testing - state is set by fixtures"""
    yield

@pytest.fixture
def create_ingestion_service(db_pool: ConnectionPool, mock_reddit_client: MagicMock) -> IngestionService:
    """Creates a Sentiment Service Instance fixture"""
    return IngestionService(
        reddit_client=mock_reddit_client,
        db_pool=db_pool,
        logger=StructuredLogger(pod="ingestion_service"),
        category="GPU",
        subreddits=["nvidia"],
        detector=DetectorFactory.get_detector(category="GPU"),
        normalizer=NormalizerFactory
    )

@pytest.fixture
def mock_logger() -> MagicMock:
    """Mocked structured logger"""
    return MagicMock(spec=StructuredLogger)

@pytest.fixture
def mock_detector() -> MagicMock:
    """Mocked product detector"""
    return MagicMock(spec=DetectorFactory.get_detector(category="GPU"))

@pytest.fixture
def mock_normalizer() -> MagicMock:
    """Mocked normalizer"""
    return MagicMock()

@pytest.fixture
def mock_ingestion_service(mock_reddit_client: MagicMock) -> IngestionService:
    """Mock ingestion service with all dependencies mocked for use in unit tests"""
    return IngestionService(
        reddit_client=mock_reddit_client,
        db_pool=MagicMock(spec=ConnectionPool),
        logger=MagicMock(spec=StructuredLogger),
        category="GPU",
        subreddits=["nvidia"],
        detector=MagicMock(spec=DetectorFactory.get_detector(category="GPU")),
        normalizer=MagicMock(spec=NormalizerFactory)
    )

@pytest.fixture
def worker_with_test_db(postgres_container: PostgresContainer, mock_reddit_client: MagicMock) -> Generator[IngestionService, None, None]:
    """
    Create a Worker instance configured to use the test database.
    Patches the connection pool to use the test container.
    """
    with patch('src.core.reddit_client_instance.createRedditClient', return_value=mock_reddit_client) as mock_reddit_client:
        with patch('src.db_utils.conn.create_connection_pool') as mock_pool:
            # Create a real connection pool to the test database
            # Convert SQLAlchemy URL to PostgreSQL URI for psycopg
            connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
            test_pool = ConnectionPool(
                conninfo=connection_url,
                min_size=1,
                max_size=5,
                open=True
            )
            mock_pool.return_value = test_pool

            worker = IngestionService(
                reddit_client=mock_reddit_client,
                db_pool=test_pool,
                logger=StructuredLogger(pod="ingestion_service"),
                category="gpu",
                subreddits=["nvidia"],
                detector=DetectorFactory.get_detector("gpu"),
                normalizer=NormalizerFactory
            )
            yield worker

            # Cleanup - truncate table after test
            with test_pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE raw_comments RESTART IDENTITY CASCADE;")
                conn.commit()

            test_pool.close()
