from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import patch
from testcontainers.postgres import PostgresContainer
from psycopg_pool import ConnectionPool
from concurrent.futures import ThreadPoolExecutor
from src.core.logger import StructuredLogger
from src.ingestion_service import IngestionService
import pytest


@pytest.fixture
def create_ingestion_service(
    db_pool: ConnectionPool, mock_reddit_client: MagicMock
) -> IngestionService:
    """Creates a Sentiment Service Instance fixture"""

    return IngestionService(
        reddit_client=mock_reddit_client,
        db_pool=db_pool,
        logger=StructuredLogger(pod="ingestion_service"),
        topic_list=["GPU"],
        subreddit_list=["nvidia"],
        fetch_executor=ThreadPoolExecutor(max_workers=1),
    )


@pytest.fixture
def mock_logger() -> MagicMock:
    """Mocked structured logger"""
    return MagicMock(spec=StructuredLogger)

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
        topic_list=["GPU"],
        subreddit_list=["nvidia"],
        fetch_executor=MagicMock(spec=ThreadPoolExecutor),
    )


@pytest.fixture
def worker_with_test_db(
    postgres_container: PostgresContainer, mock_reddit_client: MagicMock
) -> Generator[IngestionService, None, None]:
    """
    Create a Worker instance configured to use the test database.
    Patches the connection pool to use the test container.
    """
    with patch(
        "src.core.reddit_client_instance.createRedditClient", return_value=mock_reddit_client
    ) as mock_reddit_client:
        with patch("src.db_utils.conn.create_connection_pool") as mock_pool:
            # Create a real connection pool to the test database
            # Convert SQLAlchemy URL to PostgreSQL URI for psycopg
            connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
            test_pool = ConnectionPool(conninfo=connection_url, min_size=1, max_size=5, open=True)
            mock_pool.return_value = test_pool

            worker = IngestionService(
                reddit_client=mock_reddit_client,
                db_pool=test_pool,
                logger=StructuredLogger(pod="ingestion_service"),
                topic_list=["GPU"],
                subreddit_list=["nvidia"],
                fetch_executor=ThreadPoolExecutor(max_workers=1),
            )
            yield worker

            # Cleanup - truncate table after test
            with test_pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE raw_comments RESTART IDENTITY CASCADE;")
                conn.commit()

            test_pool.close()
