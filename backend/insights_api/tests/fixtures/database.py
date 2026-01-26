from typing import Generator
from sqlalchemy import text
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
async def test_engine(postgres_container: PostgresContainer) -> AsyncGenerator[AsyncEngine, None]:
    """
    Create an async SQLAlchemy engine for the test database.
    Session-scoped to reuse across tests.
    """
    connection_url = postgres_container.get_connection_url()
    async_url = connection_url.replace("postgresql+psycopg2", "postgresql+asyncpg")

    engine = create_async_engine(
        url=async_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_async_session(test_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async sessionmaker for testing."""
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


@pytest_asyncio.fixture(scope="session")
async def setup_test_database(test_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Set up the database schema once per test session."""
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
                product_topic VARCHAR(50) NOT NULL,
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
                product_topic VARCHAR(100) NOT NULL,
                sentiment_score FLOAT NOT NULL,
                created_utc TIMESTAMPTZ NOT NULL,
                UNIQUE (comment_id, product_name)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS product_rankings (
                id SERIAL PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                product_topic VARCHAR(100) NOT NULL,
                time_window VARCHAR(20) NOT NULL,
                rank INT NOT NULL,
                grade VARCHAR(2) NOT NULL,
                bayesian_score FLOAT NOT NULL,
                mention_count INT NOT NULL,
                approval_percentage INT NOT NULL,
                positive_count INT NOT NULL,
                neutral_count INT NOT NULL,
                negative_count INT NOT NULL,
                is_top_pick BOOLEAN DEFAULT FALSE,
                is_most_discussed BOOLEAN DEFAULT FALSE,
                has_limited_data BOOLEAN DEFAULT FALSE,
                UNIQUE (product_name, time_window)
            )
        """))

    yield

    async with test_engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS product_rankings, product_sentiment, raw_comments CASCADE;"))


@pytest_asyncio.fixture
async def clean_tables(
    test_async_session: async_sessionmaker[AsyncSession],
    setup_test_database: None
) -> AsyncGenerator[None, None]:
    """Clean up tables before each test to ensure isolation."""
    async with test_async_session() as session:
        await session.execute(text("TRUNCATE TABLE product_rankings, product_sentiment, raw_comments RESTART IDENTITY CASCADE;"))
        await session.commit()
    yield

@pytest_asyncio.fixture
async def seed_product_rankings(
    test_async_session: async_sessionmaker[AsyncSession],
    clean_tables: None,
    setup_test_database: None
) -> AsyncGenerator[None, None]:
    """Seed product_rankings table with test data."""
    async with test_async_session() as session:
        await session.execute(text("""
            INSERT INTO product_rankings
                (product_name, product_topic, time_window, rank, grade, bayesian_score,
                 mention_count, approval_percentage, positive_count, neutral_count,
                 negative_count, is_top_pick, is_most_discussed, has_limited_data)
            VALUES
                ('nvidia rtx 4090', 'GPU', '90d', 1, 'A', 9.5, 500, 95, 100, 10, 5, true, true, false),
                ('nvidia rtx 4080', 'GPU', '90d', 2, 'A', 8.8, 300, 88, 80, 15, 10, false, false, false),
                ('amd rx 7900 xtx', 'GPU', '90d', 3, 'B', 7.5, 200, 75, 60, 20, 15, false, false, false),
                ('nvidia rtx 4090', 'GPU', 'all_time', 1, 'A', 9.2, 1000, 92, 200, 20, 10, true, true, false)
        """))
        await session.commit()
    yield


@pytest_asyncio.fixture
async def seed_raw_comments(
    test_async_session: async_sessionmaker[AsyncSession],
    clean_tables: None,
    setup_test_database: None
) -> AsyncGenerator[None, None]:
    """Seed raw_comments table with test data."""
    async with test_async_session() as session:
        await session.execute(text("""
            INSERT INTO raw_comments
                (comment_id, post_id, comment_body, detected_products, subreddit,
                 author, score, created_utc, product_topic, sentiment_processed)
            VALUES
                ('comment_1', 'post_1', 'The RTX 4090 is amazing for gaming!', ARRAY['nvidia rtx 4090'], 'nvidia', 'user1', 150, NOW() - INTERVAL '30 days', 'GPU', true),
                ('comment_2', 'post_1', 'Great performance on the 4090', ARRAY['nvidia rtx 4090'], 'nvidia', 'user2', 100, NOW() - INTERVAL '60 days', 'GPU', true),
                ('comment_3', 'post_2', 'The 4090 runs hot but worth it', ARRAY['nvidia rtx 4090'], 'buildapc', 'user3', 75, NOW() - INTERVAL '10 days', 'GPU', true),
                ('comment_4', 'post_3', 'Old comment about 4090', ARRAY['nvidia rtx 4090'], 'nvidia', 'user4', 200, NOW() - INTERVAL '120 days', 'GPU', true),
                ('comment_5', 'post_4', 'Unprocessed comment', ARRAY['nvidia rtx 4090'], 'nvidia', 'user5', 50, NOW() - INTERVAL '5 days', 'GPU', false)
        """))
        await session.commit()
    yield