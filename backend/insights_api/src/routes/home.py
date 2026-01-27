from fastapi import Depends
from fastapi import APIRouter
from fastapi import HTTPException
from valkey.asyncio import Valkey
from src.core.settings import Settings
from src.db_utils.cache_conn import get_cache
from src.db_utils.cache_commands import get_weekly_trending_key
from src.schemas.home import TrendingTopic
from src.schemas.home import TrendingTopicsResponse

settings = Settings()

routes = APIRouter(prefix=f"/api/{settings.API_VERSION}", tags=["Production"])


@routes.get(path="/home/trending/product_topics")
async def get_trending_product_topics(
    cache: Valkey | None = Depends(get_cache),
) -> TrendingTopicsResponse:
    """Fetch the top 6 most viewed product topics based on views from users on the site"""
    if not cache:
        raise HTTPException(
            status_code=503,
            detail="Feature requires cache service (currently unavailable)",
        )

    try:
        # Get current week's trending topic cache key
        trending_key = get_weekly_trending_key()

        trending = await cache.zrevrange(trending_key, 0, 5, withscores=True)

        if not trending:
            return TrendingTopicsResponse(trending_topics=[])

        # convert valkey result, [(b'GPU', 127.0), (b'Laptop', 89.0),...] to pydantic models
        return TrendingTopicsResponse(
            trending_topics=[
                TrendingTopic(topic=topic, view_count=int(score))
                for topic, score in trending
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cache service error: {e}")
