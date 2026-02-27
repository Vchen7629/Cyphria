from typing import Any
from typing import Callable
from typing import Generator
from unittest.mock import patch
from psycopg_pool import ConnectionPool
from testcontainers.postgres import PostgresContainer
import os
os.environ.setdefault("BAYESIAN_PARAMS", "10")
from src.ranking_service import RankingService
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
                    CREATE TABLE product_sentiment (
                        id SERIAL PRIMARY KEY,
                        comment_id VARCHAR(50) NOT NULL,
                        product_name VARCHAR(100) NOT NULL,
                        product_topic VARCHAR(100) NOT NULL,
                        sentiment_score FLOAT NOT NULL,
                        created_utc TIMESTAMPTZ NOT NULL,

                        UNIQUE (comment_id, product_name)
                    );

                    CREATE TABLE product_rankings (
                        id SERIAL PRIMARY KEY,
                        product_name VARCHAR(50) NOT NULL,
                        product_topic VARCHAR(100) NOT NULL,
                        time_window VARCHAR(20) NOT NULL,

                        rank INTEGER NOT NULL,
                        grade VARCHAR(5),

                        bayesian_score DOUBLE PRECISION NOT NULL,
                        avg_sentiment DOUBLE PRECISION NOT NULL,
                        approval_percentage INT,

                        mention_count INTEGER NOT NULL,
                        positive_count INTEGER,
                        negative_count INTEGER,
                        neutral_count INTEGER,

                        is_top_pick BOOLEAN DEFAULT FALSE,
                        is_most_discussed BOOLEAN DEFAULT FALSE,
                        has_limited_data BOOLEAN DEFAULT FALSE,

                        calculation_date DATE NOT NULL,

                        UNIQUE(product_name, time_window)
                    )
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
            "TRUNCATE TABLE product_sentiment, product_rankings RESTART IDENTITY CASCADE;"
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
                "TRUNCATE TABLE product_sentiment, product_rankings RESTART IDENTITY CASCADE;"
            )
        conn.commit()

    yield pool

    pool.close()


@pytest.fixture
def mock_db_conn_lifespan(
    db_pool: ConnectionPool, create_ingestion_service: RankingService
) -> Generator[Callable[[], Any], None, None]:
    """
    Factory fixture that creates a StartService with mocked heavy dependencies.
    Patches _db_conn_lifespan then injects the test db_pool

    Usage:
        def test_something(create_worker):
            worker = create_worker()
            worker.run()
    """

    with patch.object(RankingService, "_db_conn_lifespan"):

        def _create() -> RankingService:
            service = create_ingestion_service
            service.db_pool = db_pool
            return service

        yield _create
