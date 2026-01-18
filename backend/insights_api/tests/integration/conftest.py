from sqlalchemy.ext.asyncio.engine import AsyncEngine
from src.core.logger import StructuredLogger
from src.db_utils.conn import get_session
from src.routes.category import routes as category_router
from src.routes.products import routes as product_router
from testcontainers.postgres import PostgresContainer
from typing import Any
from typing import AsyncGenerator
from typing import Generator
from typing import NamedTuple
from typing import Callable
from fastapi import FastAPI
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import os
import pytest
import asyncio

os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASS", "test_pass")


class FastAPITestClient(NamedTuple):
    client: TestClient
    app: FastAPI


@asynccontextmanager
async def null_lifespan(_app: FastAPI) -> AsyncGenerator[Any, Any]:
    """No-op lifespan for testing - state is set by fixtures"""
    yield


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """
    Start a PostgreSQL container for integration tests.
    This fixture is session-scoped so one container is shared across all tests.
    """
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def test_engine(postgres_container: PostgresContainer) -> AsyncEngine:
    """
    Create an async SQLAlchemy engine for the test database.
    Session-scoped to reuse across tests.
    """
    # Convert connection URL to async format
    connection_url = postgres_container.get_connection_url()
    async_url = connection_url.replace("postgresql+psycopg2", "postgresql+asyncpg")

    engine = create_async_engine(
        url=async_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True
    )
    return engine


@pytest.fixture(scope="session")
def test_async_session(test_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async sessionmaker for testing."""
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_database(test_engine: AsyncEngine) -> Generator[Any, Any, Any]:
    """Set up the database schema once per test session."""

    async def create_tables() -> Any:
        async with test_engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS raw_comments (
                    id SERIAL PRIMARY KEY,
                    comment_id VARCHAR(50) UNIQUE NOT NULL,
                    post_id VARCHAR(50) NOT NULL,
                    comment_body TEXT NOT NULL,
                    detected_products TEXT[] NOT NULL,
                    subreddit VARCHAR(100) NOT NULL,
                    author VARCHAR(100),
                    score INT DEFAULT 0,
                    created_utc TIMESTAMPTZ NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    ingested_at TIMESTAMPTZ DEFAULT NOW(),
                    sentiment_processed BOOLEAN DEFAULT FALSE,
                    CONSTRAINT chk_detected_products CHECK (array_length(detected_products, 1) > 0)
                )
            """))
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS product_sentiment (
                    id SERIAL PRIMARY KEY,
                    comment_id VARCHAR(50) NOT NULL,
                    product_name VARCHAR(100) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    sentiment_score FLOAT NOT NULL,
                    created_utc TIMESTAMPTZ NOT NULL,
                    UNIQUE (comment_id, product_name)
                )
            """))

    asyncio.get_event_loop().run_until_complete(create_tables())
    yield

    async def drop_tables() -> Any:
        async with test_engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS product_sentiment, raw_comments CASCADE;"))

    asyncio.get_event_loop().run_until_complete(drop_tables())


@pytest.fixture
def clean_tables(test_async_session: async_sessionmaker[AsyncSession]) -> Generator[Any, Any]:
    """Clean up tables before each test to ensure isolation."""

    async def truncate() -> None:
        async with test_async_session() as session:
            await session.execute(text("TRUNCATE TABLE product_sentiment, raw_comments RESTART IDENTITY CASCADE;"))
            await session.commit()

    asyncio.get_event_loop().run_until_complete(truncate())
    yield


@pytest.fixture
def fastapi_client(
    test_async_session: async_sessionmaker[AsyncSession],
    clean_tables: Callable[[], Any]
) -> Generator[FastAPITestClient, None, None]:
    """FastAPI TestClient with test database session."""
    test_app = FastAPI(lifespan=null_lifespan)
    test_app.include_router(category_router)
    test_app.include_router(product_router)

    test_app.state.async_session = test_async_session
    test_app.state.logger = StructuredLogger(pod="insights_api_test")

    # Override the get_session dependency to use test database
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with test_async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    test_app.dependency_overrides[get_session] = override_get_session

    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield FastAPITestClient(client=client, app=test_app)
