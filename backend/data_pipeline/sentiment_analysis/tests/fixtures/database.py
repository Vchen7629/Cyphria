from typing import Any
from typing import Generator
from datetime import datetime
from datetime import timezone
from psycopg_pool import ConnectionPool
from testcontainers.postgres import PostgresContainer
import pytest
import psycopg


@pytest.fixture
def single_comment() -> dict[str, Any]:
    """Fixture for single comment instance"""
    return {
        "comment_id": "test_comment_1",
        "post_id": "test_post_1",
        "comment_body": "This is a test comment about RTX 4090",
        "detected_products": ["rtx 4090"],
        "subreddit": "nvidia",
        "author": "test_user",
        "score": 42,
        "created_utc": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        "product_topic": "GPU",
    }


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
                        product_topic VARCHAR(50) NOT NULL,

                        -- Processing tracking
                        ingested_at TIMESTAMPTZ DEFAULT NOW(),
                        sentiment_processed BOOLEAN DEFAULT FALSE,

                        CONSTRAINT chk_detected_products CHECK (array_length(detected_products, 1) > 0)
                    );

                    CREATE TABLE product_sentiment (
                        id SERIAL PRIMARY KEY,
                        comment_id VARCHAR(50) NOT NULL,
                        product_name VARCHAR(100) NOT NULL,
                        product_topic VARCHAR(100) NOT NULL,
                        sentiment_score FLOAT NOT NULL,
                        created_utc TIMESTAMPTZ NOT NULL,

                        UNIQUE (comment_id, product_name)
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
