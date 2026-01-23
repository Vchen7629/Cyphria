from typing import Any
from fastapi import FastAPI
from contextlib import asynccontextmanager
from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
import os
os.environ.setdefault("PRODUCT_CATEGORY", "GPU")
os.environ.setdefault("REDDIT_API_CLIENT_ID", "reddit_id")
os.environ.setdefault("REDDIT_API_CLIENT_SECRET", "reddit_secret")
os.environ.setdefault("REDDIT_ACCOUNT_USERNAME", "username")
os.environ.setdefault("REDDIT_ACCOUNT_PASSWORD", "password")
from src.core.logger import StructuredLogger
from src.ingestion_service import IngestionService
from src.product_utils.detector_factory import DetectorFactory
from src.product_utils.normalizer_factory import NormalizerFactory
import pytest

@asynccontextmanager
async def null_lifespan(_app: FastAPI) -> Any:
    """No-op lifespan for testing - state is set by fixtures"""
    yield

@pytest.fixture
def create_ingestion_service(db_pool: ConnectionPool, mock_reddit_client: MagicMock) -> IngestionService:
    """Creates a Sentiment Service Instance fixture"""
    return IngestionService(
        reddit_client=mock_reddit_client,
        db_pool=db_pool,
        logger=StructuredLogger(pod="ingestion_service"),
        category="GPU",
        subreddits=["nvidia"],
        detector=DetectorFactory.get_detector(category="GPU"),
        normalizer=NormalizerFactory
    )

@pytest.fixture
def mock_logger() -> MagicMock:
    """Mocked structured logger"""
    return MagicMock(spec=StructuredLogger)

@pytest.fixture
def mock_detector() -> MagicMock:
    """Mocked product detector"""
    return MagicMock(spec=DetectorFactory.get_detector(category="GPU"))

@pytest.fixture
def mock_normalizer() -> MagicMock:
    """Mocked normalizer"""
    return MagicMock()

@pytest.fixture
def mock_ingestion_service(mock_reddit_client: MagicMock) -> IngestionService:
    """Mock ingestion service with all dependencies mocked for use in unit tests"""
    return IngestionService(
        reddit_client=mock_reddit_client,
        db_pool=MagicMock(spec=ConnectionPool),
        logger=MagicMock(spec=StructuredLogger),
        category="GPU",
        subreddits=["nvidia"],
        detector=MagicMock(spec=DetectorFactory.get_detector(category="GPU")),
        normalizer=MagicMock(spec=NormalizerFactory)
    )