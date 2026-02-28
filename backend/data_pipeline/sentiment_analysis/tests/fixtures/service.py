from datetime import datetime
from datetime import timezone
from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
from shared_core.logger import StructuredLogger
from pipeline_types.data_pipeline import JobStatus
from src.sentiment_service import SentimentService
from src.preprocessing.sentiment_analysis import Aspect_Based_Sentiment_Analysis
import time
import pytest


@pytest.fixture
def mock_absa() -> MagicMock:
    """
    Mock ABSA model that returns fixed sentiment scores.
    Returns list of (None, sentiment_score) tuples matching input length.
    """
    mock = MagicMock()

    def mock_sentiment_analysis(pairs: list[tuple[str, str]]) -> list[tuple[None, float]]:
        time.sleep(0.5)
        return [(None, 0.5) for _ in pairs]

    mock.SentimentAnalysis.side_effect = mock_sentiment_analysis
    return mock


@pytest.fixture
def create_sentiment_service(db_pool: ConnectionPool, mock_absa: MagicMock) -> SentimentService:
    """Creates a Sentiment Service Instance fixture"""
    return SentimentService(
        logger=StructuredLogger(pod="sentiment_analysis"),
        product_topic="GPU",
        db_pool=db_pool,
        model=mock_absa,
    )


@pytest.fixture
def mock_sentiment_service() -> SentimentService:
    """Mock sentiment service with all dependencies mocked for use in unit tests"""
    return SentimentService(
        db_pool=MagicMock(spec=ConnectionPool),
        logger=MagicMock(spec=StructuredLogger),
        product_topic="GPU",
        model=MagicMock(spec=Aspect_Based_Sentiment_Analysis),
    )


@pytest.fixture
def mock_job() -> MagicMock:
    return MagicMock(
        product_topic="GPU",
        status=JobStatus.RUNNING,
        started_at=datetime.now(tz=timezone.utc),
        completed_at=None,
        result=None,
        error=None,
    )
