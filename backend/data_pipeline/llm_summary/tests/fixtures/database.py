from typing import Any
from typing import Generator
from datetime import datetime
from datetime import timezone
from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
from testcontainers.postgres import PostgresContainer
import pytest
import psycopg


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

                    CREATE TABLE product_summaries (
                        id SERIAL PRIMARY KEY,
                        product_name VARCHAR(100) NOT NULL,
                        tldr VARCHAR(50) NOT NULL,
                        time_window VARCHAR(20) NOT NULL,
                        model_used VARCHAR(30) NOT NULL,
                        generated_at TIMESTAMPTZ NOT NULL,

                        UNIQUE (product_name, time_window)
                    );
                """)
            conn.commit()

        yield postgres


@pytest.fixture
def db_connection(
    postgres_container: PostgresContainer,
) -> Generator[psycopg.Connection, None, None]:
    """
    Create a fresh database connection for each test.
    Cleans up tables before each test to ensure isolation.
    """
    connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
    conn = psycopg.connect(connection_url)

    # Cleanup BEFORE test to ensure clean state
    with conn.cursor() as cursor:
        cursor.execute(
            "TRUNCATE TABLE product_sentiment, raw_comments, product_summaries RESTART IDENTITY CASCADE;"
        )
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
    pool = ConnectionPool(conninfo=connection_url, min_size=1, max_size=5, open=True)
    with pool.connection() as conn:
        # Rollback any failed transaction first
        if conn.info.transaction_status != psycopg.pq.TransactionStatus.IDLE:
            conn.rollback()

        with conn.cursor() as cursor:
            cursor.execute(
                "TRUNCATE TABLE product_sentiment, raw_comments RESTART IDENTITY CASCADE;"
            )
        conn.commit()

    yield pool

    pool.close()


@pytest.fixture
def single_product_summary() -> dict[str, Any]:
    """Fixture for single product summary row"""
    return {
        "product_name": "rtx 4090",
        "tldr": "rtx 4090 tldr",
        "time_window": "all_time",
        "model_used": "chatgpt-5.2",
    }


@pytest.fixture
def single_product_sentiment() -> dict[str, Any]:
    """Fixture for single comment row"""
    return {
        "comment_id": "test_comment_1",
        "product_name": "rtx 4090",
        "category": "GPU",
        "sentiment_score": 0.98,
        "created_utc": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    }


@pytest.fixture
def single_raw_comment() -> dict[str, Any]:
    """Fixture for single raw comment row"""
    return {
        "comment_id": "test_comment_1",
        "post_id": "test_post_1",
        "comment_body": "This is a test comment about RTX 4090",
        "detected_products": ["rtx 4090"],
        "subreddit": "nvidia",
        "author": "test_user",
        "score": 42,
        "created_utc": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        "category": "GPU",
    }


@pytest.fixture
def mock_cursor() -> MagicMock:
    """Mock database cursor for unit tests."""
    cursor = MagicMock()
    cursor.fetchall.return_value = []  # type: ignore
    cursor.fetchone.return_value = None
    cursor.execute.return_value = None
    cursor.__enter__.return_value = cursor
    cursor.__exit__.return_value = None
    return cursor


@pytest.fixture
def mock_db_connection(mock_cursor: MagicMock) -> Generator[MagicMock, None, None]:
    """Mock database connection"""
    conn = MagicMock()
    conn.cursor.return_value = mock_cursor
    conn.commit.return_value = None
    conn.rollback.return_value = None
    conn.close.return_value = None
    conn.closed = False

    yield conn
