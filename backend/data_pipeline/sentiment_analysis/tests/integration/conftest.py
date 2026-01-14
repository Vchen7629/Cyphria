from unittest.mock import patch
from typing import Callable
from unittest.mock import MagicMock
import pytest
import psycopg
from testcontainers.postgres import PostgresContainer
from typing import Generator, Any
from psycopg_pool import ConnectionPool
from datetime import datetime, timezone
from src.worker import StartService
import os
import time

os.environ.setdefault("PRODUCT_CATEGORY", "GPU")
os.environ.setdefault("POLLING_INTERVAL", "5.0")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASS", "test_pass")

@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """
    Start a PostgreSQL container for integration tests.
    This fixture is session-scoped so one container is shared across all tests.
    """
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

                    CREATE TABLE product_sentiment (
                        id SERIAL PRIMARY KEY,
                        comment_id VARCHAR(50) NOT NULL,
                        product_name VARCHAR(100) NOT NULL,
                        category VARCHAR(100) NOT NULL,
                        sentiment_score FLOAT NOT NULL,
                        created_utc TIMESTAMPTZ NOT NULL,

                        UNIQUE (comment_id, product_name)
                    );
                """)
            conn.commit()

        yield postgres


@pytest.fixture
def db_connection(postgres_container: PostgresContainer) -> Generator[psycopg.Connection, None, None]:
    """
    Create a fresh database connection for each test.
    Cleans up tables before each test to ensure isolation.
    """
    connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
    conn = psycopg.connect(connection_url)

    # Cleanup BEFORE test to ensure clean state
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE product_sentiment, raw_comments RESTART IDENTITY CASCADE;")
    conn.commit()

    yield conn

    if not conn.closed:
        if conn.info.transaction_status != psycopg.pq.TransactionStatus.IDLE:
            conn.rollback()
        conn.close()


@pytest.fixture
def db_pool(postgres_container: PostgresContainer) -> Generator[ConnectionPool, None, None]:
    """
    Create a connection pool for testing pool-based operations. clean up tables after each test
    """
    # Convert SQLAlchemy URL to PostgreSQL URI for psycopg
    connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
    pool = ConnectionPool(
        conninfo=connection_url,
        min_size=1,
        max_size=5,
        open=True
    )
    with pool.connection() as conn:
        # Rollback any failed transaction first
        if conn.info.transaction_status != psycopg.pq.TransactionStatus.IDLE:
            conn.rollback()

        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE product_sentiment, raw_comments RESTART IDENTITY CASCADE;")
        conn.commit()
        
    yield pool

    pool.close()
    

@pytest.fixture
def single_comment() -> dict[str, Any]:
    """Fixture for single comment instance"""
    return {
        'comment_id': 'test_comment_1',
        'post_id': 'test_post_1',
        'comment_body': 'This is a test comment about RTX 4090',
        'detected_products': ['rtx 4090'],
        'subreddit': 'nvidia',
        'author': 'test_user',
        'score': 42,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'category': 'GPU'
    }

@pytest.fixture
def mock_absa() -> MagicMock:
    """
    Mock ABSA model that returns fixed sentiment scores.
    Returns list of (None, sentiment_score) tuples matching input length.
    """
    mock = MagicMock()

    def mock_sentiment_analysis(pairs: list[tuple[str, str]]) -> list[tuple[None, float]]:
        time.sleep(0.5)
        return [(None, 0.5) for _ in pairs]

    mock.SentimentAnalysis.side_effect = mock_sentiment_analysis
    return mock


@pytest.fixture
def create_worker(db_pool: ConnectionPool, mock_absa: MagicMock) -> Generator[Callable[[], Any], None, None]:
    """
    Factory fixture that creates a StartService with mocked heavy dependencies.
    Patches _database_conn_lifespan, _initialize_absa_model, and _cleanup,
    then injects the test db_pool and mock_absa.

    Usage:
        def test_something(create_worker):
            worker = create_worker()
            worker.run()
    """

    with patch.object(StartService, '_database_conn_lifespan'), \
         patch.object(StartService, '_initialize_absa_model'), \
         patch.object(StartService, '_cleanup'):

        def _create() -> StartService:
            service = StartService()
            service.db_pool = db_pool
            service.ABSA = mock_absa
            return service

        yield _create