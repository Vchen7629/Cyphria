from src.core.settings import Settings
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine

settings = Settings()

DATABASE_URL = settings.database_url

engine: AsyncEngine = create_async_engine(
    url=DATABASE_URL,
    pool_size=10,
    max_overflow=20, 
    pool_pre_ping=True, # health check connections before use
    pool_recycle=3600 # recycle connections after 1 hour
)

# session factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# creates a short lived session from the sessionmaker factory
# used per request
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()