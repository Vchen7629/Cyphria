from typing import Any
from typing import Generator
from sqlalchemy import text
from datetime import datetime
from datetime import timezone
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from testcontainers.postgres import PostgresContainer
import pytest
import pytest_asyncio


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """
    Start a PostgreSQL container for integration tests.
    This fixture is session-scoped so one container is shared across all tests.
    """
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


@pytest_asyncio.fixture(scope="session")
async def test_engine(
    postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    """
    Create an async SQLAlchemy engine for the test database.
    Session-scoped to reuse across tests.
    """
    connection_url = postgres_container.get_connection_url()
    async_url = connection_url.replace("postgresql+psycopg2", "postgresql+asyncpg")

    engine = create_async_engine(
        url=async_url, pool_size=5, max_overflow=10, pool_pre_ping=True
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_async_session(
    test_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create an async sessionmaker for testing."""
    return async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )


@pytest_asyncio.fixture(scope="session")
async def setup_test_database(test_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Set up the database schema once per test session."""
    async with test_engine.begin() as conn:
        await conn.execute(
            text("""
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
                product_topic VARCHAR(50) NOT NULL,
                ingested_at TIMESTAMPTZ DEFAULT NOW(),
                sentiment_processed BOOLEAN DEFAULT FALSE,
                CONSTRAINT chk_detected_products CHECK (array_length(detected_products, 1) > 0)
            )
        """)
        )
        await conn.execute(
            text("""
            CREATE TABLE IF NOT EXISTS product_sentiment (
                id SERIAL PRIMARY KEY,
                comment_id VARCHAR(50) NOT NULL,
                product_name VARCHAR(100) NOT NULL,
                product_topic VARCHAR(100) NOT NULL,
                sentiment_score FLOAT NOT NULL,
                created_utc TIMESTAMPTZ NOT NULL,
                UNIQUE (comment_id, product_name)
            )
        """)
        )
        await conn.execute(
            text("""
            CREATE TABLE IF NOT EXISTS product_rankings (
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
                UNIQUE (product_name, time_window)
            )
        """)
        )

    yield

    async with test_engine.begin() as conn:
        await conn.execute(
            text(
                "DROP TABLE IF EXISTS product_rankings, product_sentiment, raw_comments CASCADE;"
            )
        )


@pytest_asyncio.fixture
async def clean_tables(
    test_async_session: async_sessionmaker[AsyncSession], setup_test_database: None
) -> AsyncGenerator[None, None]:
    """Clean up tables before each test to ensure isolation."""
    async with test_async_session() as session:
        await session.execute(
            text(
                "TRUNCATE TABLE product_rankings, product_sentiment, raw_comments RESTART IDENTITY CASCADE;"
            )
        )
        await session.commit()
    yield


@pytest.fixture
def single_product_ranking_row() -> dict[str, Any]:
    """Single row in the product ranking table"""
    return {
        "product_name": "nvidia rtx 4080",
        "product_topic": "GPU",
        "time_window": "all_time",
        "rank": 1,
        "grade": "S",
        "bayesian_score": 0.96,
        "avg_sentiment": 0.96,
        "approval_percentage": 100,
        "mention_count": 100,
        "positive_count": 100,
        "negative_count": 0,
        "neutral_count": 0,
        "is_top_pick": True,
        "is_most_discussed": False,
        "has_limited_data": False,
        "calculation_date": datetime.now(timezone.utc),
    }


@pytest.fixture
def single_raw_comment() -> dict[str, Any]:
    """Single row in the raw_comments table"""
    return {
        "comment_id": "comment_1",
        "post_id": "post_1",
        "comment_body": "The RTX 4090 is amazing for gaming!",
        "detected_products": ["nvidia rtx 4090"],
        "subreddit": "nvidia",
        "author": "user1",
        "score": 150,
        "created_utc": datetime.now(timezone.utc),
        "product_topic": "GPU",
        "sentiment_processed": True,
    }
