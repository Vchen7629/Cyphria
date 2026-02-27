from typing import Any
from typing import TypeVar
from typing import Optional
from typing import Callable
from datetime import datetime
from pydantic import BaseModel
from valkey.asyncio import Valkey
from valkey.typing import ResponseT
from shared_core.logger import StructuredLogger
from src.middleware.metrics import cache_operation_duration
import time

T = TypeVar("T", bound=BaseModel)


async def get_cache_value(
    cache: Valkey,
    cache_key: str,
    logger: StructuredLogger,
    response_model: type[T],
) -> Optional[T]:
    """
    Fetch the value of a cache_key from the caching layer (Valkey)

    Args:
        cache: the cache_client connection
        cache_key: the key in the cache with the values we are trying to fetch
        logger: StructuredLogger for logging
        response_model: pydantic type class we are returning as a api response

    Returns:
        the pydantic type class with api response or None if not found/error
    """
    start_time = time.perf_counter()
    cached_data: Optional[ResponseT] = None
    try:
        cached_data = await cache.get(cache_key)
        return response_model.model_validate(cached_data) if cached_data else None
    except Exception as e:
        logger.warning(
            event_type="insights_api run",
            message=f"Cache read failed, falling back to db: {e}",
        )
        return None
    finally:
        duration = time.perf_counter() - start_time
        cache_operation_duration.labels(
            operation="get", hit=str(cached_data is not None)
        ).observe(duration)


async def set_cache_value(
    cache: Valkey,
    cache_key: str,
    value: BaseModel,
    ttl_seconds: int,
    logger: StructuredLogger,
    on_cache_write: Optional[Callable[[Valkey], Any]] = None,
) -> None:
    """
    Set value in cache (Valkey) with optional side effects

    Args:
        cache: Cache (Valkey) client connection
        cache_key: cache_key to set in the db
        value: Pydantic Model to cache
        ttl_seconds: Expiry time in seconds
        logger: StructuredLogger instance
        on_cache_write: Optional async callback for additional cache ops
    """
    start_time = time.perf_counter()
    try:
        await cache.setex(cache_key, ttl_seconds, value.model_dump_json())
        # Execute optional side effect like updating trending sorted set
        if on_cache_write:
            await on_cache_write(cache)
    except Exception as e:
        logger.warning(
            event_type="insights_api run",
            message=f"Cache write failed for key {cache_key}: {e}",
        )
    finally:
        duration = time.perf_counter() - start_time
        cache_operation_duration.labels(operation="set", hit="true").observe(duration)


def get_weekly_trending_key() -> str:
    """
    Generate weekly trending key that auto-resets each week

    Returns:
        key like "trending:topics:2026-W04"
    """
    week_info = datetime.now().isocalendar()

    return f"trending:topics:{week_info[0]}-W{week_info[1]}"


async def increment_trending_topic(
    cache: Valkey,
    topic: str,
    client_ip: str,
    weekly_ttl: int = 604800,  # 7 days represented in seconds
) -> None:
    """
    Increment topic view count in weekly trending sorted set
    only increments if ip is different, prevents refresh spam

    Args:
        cache: cache (Valkey) client connection
        topic: topic name to increment
        client_ip: client ip used to make sure it only increments with unique ips
        weekly_ttl: TTL for trending key (default is 7 days)
    """
    week_info = datetime.now().isocalendar()
    view_key: str = f"viewed:{topic}:{client_ip}:{week_info[1]}"

    is_new_view = await cache.set(view_key, "1", ex=weekly_ttl, nx=True)
    if is_new_view:
        trending_key = get_weekly_trending_key()
        await cache.zincrby(trending_key, 1, topic)
        await cache.expire(trending_key, weekly_ttl)
