from src.core.types import ProductScore
from unittest.mock import patch
from typing import Callable
from unittest.mock import MagicMock
import pytest
import psycopg
from testcontainers.postgres import PostgresContainer
from typing import Generator, Any
from psycopg_pool import ConnectionPool
from datetime import datetime, timezone
import os
import time

os.environ.setdefault("PRODUCT_CATEGORY", "GPU")
os.environ.setdefault("TIME_WINDOWS", "all_time")
os.environ.setdefault("BAYESIAN_PARAMS", "10")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASS", "test_pass")

from src.worker import RankingCalculatorWorker

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
                        category VARCHAR(100) NOT NULL,
                        sentiment_score FLOAT NOT NULL,
                        created_utc TIMESTAMPTZ NOT NULL,

                        UNIQUE (comment_id, product_name)
                    );

                    CREATE TABLE product_rankings (
                        id SERIAL PRIMARY KEY,
                        product_name VARCHAR(50) NOT NULL,
                        category VARCHAR(100) NOT NULL,
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
def db_connection(postgres_container: PostgresContainer) -> Generator[psycopg.Connection, None, None]:
    """
    Create a fresh database connection for each test.
    Cleans up tables before each test to ensure isolation.
    """
    connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
    conn = psycopg.connect(connection_url)

    # Cleanup BEFORE test to ensure clean state
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE product_sentiment, product_rankings RESTART IDENTITY CASCADE;")
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
            cursor.execute("TRUNCATE TABLE product_sentiment, product_rankings RESTART IDENTITY CASCADE;")
        conn.commit()
        
    yield pool

    pool.close()

@pytest.fixture
def mock_db_conn_lifespan(db_pool: ConnectionPool) -> Generator[Callable[[], Any], None, None]:
    """
    Factory fixture that creates a StartService with mocked heavy dependencies.
    Patches _db_conn_lifespan then injects the test db_pool

    Usage:
        def test_something(create_worker):
            worker = create_worker()
            worker.run()
    """

    with patch.object(RankingCalculatorWorker, '_db_conn_lifespan'):
        def _create() -> RankingCalculatorWorker:
            service = RankingCalculatorWorker()
            service.db_pool = db_pool
            return service

        yield _create
    
@pytest.fixture
def single_sentiment_comment() -> dict[str, Any]:
    """Fixture for single sentiment comment instance"""
    return {
        'comment_id': 'test_comment_1',
        'product_name': 'rtx 4090',
        'category': 'GPU',
        'sentiment_score': 0.89,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    }

@pytest.fixture
def single_product_score_comment() -> ProductScore:
    """Fixture for single Product score Object"""
    return ProductScore(
        product_name="rtx 4090",
        category="GPU",
        time_window="all_time",
        rank=1,
        grade="S",
        bayesian_score=0.96,
        avg_sentiment=0.96,
        approval_percentage=100,
        mention_count=100,
        positive_count=100,
        negative_count=0,
        neutral_count=0,
        is_top_pick=True,
        is_most_discussed=False,
        has_limited_data=False,
        calculation_date=datetime.now(timezone.utc)
    )