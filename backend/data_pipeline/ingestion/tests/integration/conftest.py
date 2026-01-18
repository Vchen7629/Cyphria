from typing import Any
from src.product_utils.normalizer_factory import NormalizerFactory
from src.product_utils.detector_factory import DetectorFactory
from src.core.logger import StructuredLogger
from unittest.mock import MagicMock
import os
os.environ.setdefault("PRODUCT_CATEGORY", "GPU")
os.environ.setdefault("REDDIT_API_CLIENT_ID", "reddit_id")
os.environ.setdefault("REDDIT_API_CLIENT_SECRET", "reddit_secret")
os.environ.setdefault("REDDIT_ACCOUNT_USERNAME", "username")
os.environ.setdefault("REDDIT_ACCOUNT_PASSWORD", "password")
from src.worker import IngestionService
from typing import Callable
import pytest
import psycopg
from testcontainers.postgres import PostgresContainer
from typing import Generator, NamedTuple
from psycopg_pool import ConnectionPool
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.routes import router as base_router


class FastAPITestClient(NamedTuple):
    client: TestClient
    app: FastAPI


@asynccontextmanager
async def null_lifespan(_app: FastAPI) -> Any:
    """No-op lifespan for testing - state is set by fixtures"""
    yield


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """ Start a PostgreSQL container for integration tests."""
    with PostgresContainer("postgres:16") as postgres:
        # Set up the schema
        # Convert SQLAlchemy URL to PostgreSQL URI for psycopg
        connection_url = postgres.get_connection_url().replace("+psycopg2", "")
        with psycopg.connect(connection_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE raw_comments (
                        id SERIAL PRIMARY KEY,
                        comment_id VARCHAR(50) UNIQUE NOT NULL,
                        post_id VARCHAR(50) NOT NULL,

                        -- Comment content
                        comment_body TEXT NOT NULL,
                        detected_products TEXT[] NOT NULL,

                        -- Metadata
                        subreddit VARCHAR(100) NOT NULL,
                        author VARCHAR(100),
                        score INT DEFAULT 0,
                        created_utc TIMESTAMPTZ NOT NULL,
                        category VARCHAR(50) NOT NULL,

                        -- Processing tracking
                        ingested_at TIMESTAMPTZ DEFAULT NOW(),
                        sentiment_processed BOOLEAN DEFAULT FALSE,

                        CONSTRAINT chk_detected_products CHECK (array_length(detected_products, 1) > 0)
                    );
                """)
            conn.commit()

        yield postgres


@pytest.fixture
def db_connection(postgres_container: PostgresContainer) -> Generator[psycopg.Connection, None, None]:
    """
    Create a fresh database connection for each test.
    Cleans up the table after each test.
    """
    # Convert SQLAlchemy URL to PostgreSQL URI for psycopg
    connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
    conn = psycopg.connect(connection_url)
    yield conn

    # Cleanup after test
    # Rollback any failed transaction first
    if conn.info.transaction_status != psycopg.pq.TransactionStatus.IDLE:
        conn.rollback()

    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE raw_comments RESTART IDENTITY CASCADE;")
    conn.commit()
    conn.close()


@pytest.fixture(scope="module")
def db_pool(postgres_container: PostgresContainer) -> Generator[ConnectionPool, None, None]:
    """
    Create a connection pool for testing pool-based operations.
    """
    # Convert SQLAlchemy URL to PostgreSQL URI for psycopg
    connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
    pool = ConnectionPool(
        conninfo=connection_url,
        min_size=1,
        max_size=5,
        open=True
    )
    yield pool

    pool.close()

@pytest.fixture(autouse=True)
def clean_db(db_pool: ConnectionPool) -> Generator[None, None, None]:
    """Auto-use fixture that wipes the table before each test for test isolation"""
    with db_pool.connection() as conn:
        # Rollback any failed transaction first
        if conn.info.transaction_status != psycopg.pq.TransactionStatus.IDLE:
            conn.rollback()

        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE raw_comments RESTART IDENTITY CASCADE;")
        conn.commit()
    
    yield

@pytest.fixture
def mock_reddit_client() -> MagicMock:
    """Mock reddit client"""
    client = MagicMock()
    client.user.me.return_value = MagicMock(name="test_user")
    return client

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
def fastapi_client(db_pool: ConnectionPool, mock_reddit_client: MagicMock) -> Generator[FastAPITestClient, None, None]:
    """Fastapi TestClient with mocked heavy dependencies"""
    test_app = FastAPI(lifespan=null_lifespan)
    test_app.include_router(base_router)

    test_app.state.db_pool = db_pool
    test_app.state.reddit_client = mock_reddit_client
    test_app.state.logger = StructuredLogger(pod="ingestion_service_test")
    test_app.state.category = "GPU"
    test_app.state.subreddits = ["nvidia"]
    test_app.state.detector = DetectorFactory.get_detector("GPU")
    test_app.state.normalizer = NormalizerFactory

    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield FastAPITestClient(client=client, app=test_app)