from typing import Any
from fastapi import FastAPI
from datetime import datetime
from datetime import timezone
from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
from contextlib import asynccontextmanager
import os

os.environ.setdefault("BAYESIAN_PARAMS", "10")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASS", "test_pass")
from src.api.schemas import ProductScore
from src.core.logger import StructuredLogger
from src.ranking_service import RankingService
import pytest


@asynccontextmanager
async def null_lifespan(_app: FastAPI) -> Any:
    """No-op lifespan for testing - state is set by fixtures"""
    yield


@pytest.fixture
def create_ranking_service(db_pool: ConnectionPool) -> RankingService:
    """Creates a Sentiment Service Instance fixture"""
    return RankingService(
        db_pool=db_pool,
        logger=StructuredLogger(pod="ranking_service"),
        product_topic="GPU",
        time_window="all_time",
    )


@pytest.fixture
def mock_ranking_service() -> RankingService:
    """Mock ingestion service with all dependencies mocked for use in unit tests"""
    return RankingService(
        db_pool=MagicMock(spec=ConnectionPool),
        logger=MagicMock(spec=StructuredLogger),
        product_topic="GPU",
        time_window="all_time",
    )


@pytest.fixture
def single_sentiment_comment() -> dict[str, Any]:
    """Fixture for single sentiment comment instance"""
    return {
        "comment_id": "test_comment_1",
        "product_name": "rtx 4090",
        "product_topic": "GPU",
        "sentiment_score": 0.89,
        "created_utc": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    }


@pytest.fixture
def single_product_score_comment() -> ProductScore:
    """Fixture for single Product score Object"""
    return ProductScore(
        product_name="rtx 4090",
        product_topic="GPU",
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
        calculation_date=datetime.now(timezone.utc),
    )
