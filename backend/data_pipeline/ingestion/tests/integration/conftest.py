import os
os.environ.setdefault("PRODUCT_CATEGORY", "GPU")
from src.worker import Worker
from unittest.mock import patch
from typing import Callable
import pytest
import psycopg
from testcontainers.postgres import PostgresContainer
from typing import Generator
from psycopg_pool import ConnectionPool


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
def create_worker(db_pool: ConnectionPool) -> Generator[Callable[[], Worker], None, None]:
    """
    Factory fixture that creates an ingestion Worker with mocked heavy dependencies.
    Patches _database_conn_lifespan, _cleanup, and expensive init calls, then injects the test db_pool.

    Usage:
        def test_something(create_worker):
            worker = create_worker()
            worker.run()
    """

    with patch.object(Worker, '_database_conn_lifespan'), \
         patch.object(Worker, '_cleanup'), \
         patch('src.worker.createRedditClient'), \
         patch('src.worker.category_to_subreddit_mapping', return_value=['test_subreddit']), \
         patch('src.worker.DetectorFactory.get_detector'):

        def _create() -> Worker:
            service = Worker()
            service.db_pool = db_pool
            return service

        yield _create
