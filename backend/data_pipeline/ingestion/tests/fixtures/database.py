from typing import Any
from typing import Generator
from datetime import datetime
from datetime import timezone
from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
from testcontainers.postgres import PostgresContainer
import pytest
import psycopg

@pytest.fixture()
def mock_raw_comment() -> dict[str, Any]:
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