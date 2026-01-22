from src.core.logger import StructuredLogger
from unittest.mock import patch
from unittest.mock import MagicMock
from testcontainers.postgres import PostgresContainer
from typing import Any
from typing import Callable
from typing import Generator
from typing import NamedTuple
from psycopg_pool import ConnectionPool
from datetime import datetime
from datetime import timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager
from src.worker import LLMSummaryWorker
from src.api.routes import router as base_router
import os
import time
import pytest
import psycopg
os.environ.setdefault("PRODUCT_CATEGORY", "GPU")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASS", "test_pass")

class FastAPITestClient(NamedTuple):
    client: TestClient
    app: FastAPI

@asynccontextmanager
async def null_lifespan(_app: FastAPI) -> Any:
    """No-op lifespan for testing - state is set by fixtures"""
    yield

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
def db_connection(postgres_container: PostgresContainer) -> Generator[psycopg.Connection, None, None]:
    """
    Create a fresh database connection for each test.
    Cleans up tables before each test to ensure isolation.
    """
    connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
    conn = psycopg.connect(connection_url)

    # Cleanup BEFORE test to ensure clean state
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE product_sentiment, raw_comments, product_summaries RESTART IDENTITY CASCADE;")
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
def single_product_sentiment() -> dict[str, Any]:
    """Fixture for single comment instance"""
    return {
        'comment_id': 'test_comment_1',
        'product_name': 'rtx 4090',
        'category': 'GPU',
        'sentiment_score': 0.98,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    }

@pytest.fixture()
def mock_openai_client() -> MagicMock:
    """Mock OpenAi client and response"""
    mock_client = MagicMock()

    mock_response = MagicMock()
    mock_response.output_text = "TLDR: This is a test summary from the mock LLM client"

    mock_client.responses.create.return_value = mock_response

    return mock_client

@pytest.fixture
def fastapi_client(db_pool: ConnectionPool, mock_openai_client: MagicMock) -> Generator[FastAPITestClient, None, None]:
    """Fastapi TestClient with mocked heavy dependencies"""
    test_app = FastAPI(lifespan=null_lifespan)
    test_app.include_router(base_router)

    test_app.state.db_pool = db_pool
    test_app.state.logger = StructuredLogger(pod="ingestion_service_test")
    test_app.state.llm_model_name = "gpt-5.2"
    test_app.state.llm_client = mock_openai_client

    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield FastAPITestClient(client=client, app=test_app)

@pytest.fixture
def create_llm_summary_service(db_pool: ConnectionPool, mock_openai_client: MagicMock) -> LLMSummaryWorker:
    """Creates a llm_summary service Instance fixture"""
    return LLMSummaryWorker(
        logger=StructuredLogger(pod="sentiment_analysis"),
        time_window="all_time",
        db_pool=db_pool,
        llm_model_name="gpt-5.2",
        llm_client=mock_openai_client
    )