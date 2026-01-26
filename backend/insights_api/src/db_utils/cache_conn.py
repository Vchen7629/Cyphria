from typing import Optional
from valkey.asyncio import Valkey
from valkey.asyncio import ConnectionPool
from src.core.settings import Settings

settings = Settings()

cache_pool = ConnectionPool(
    host=settings.CACHE_HOST,
    port=settings.CACHE_PORT,
    max_connections=settings.MAX_CONNECTIONS,
    decode_responses=True
)

cache_client = Valkey(connection_pool=cache_pool)

async def get_cache() -> Optional[Valkey]:
    """Single client instance to be reused across all requests"""
    return cache_client