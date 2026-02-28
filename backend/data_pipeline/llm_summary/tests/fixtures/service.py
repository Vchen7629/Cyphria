from datetime import timezone
from datetime import datetime
from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
from shared_core.logger import StructuredLogger
from src.summary_service import LLMSummaryService
from pipeline_types.data_pipeline import JobStatus
import pytest


@pytest.fixture
def create_summary_service(
    db_pool: ConnectionPool, mock_openai_client: MagicMock
) -> LLMSummaryService:
    """Creates a llm_summary service Instance fixture"""
    return LLMSummaryService(
        logger=StructuredLogger(pod="llm_summary"),
        time_window="all_time",
        db_pool=db_pool,
        llm_model_name="gpt-5.2",
        llm_client=mock_openai_client,
    )


@pytest.fixture
def mock_summary_service(mock_openai_client: MagicMock) -> LLMSummaryService:
    """Mock summary service with all dependencies mocked for use in unit tests"""
    return LLMSummaryService(
        db_pool=MagicMock(spec=ConnectionPool),
        logger=MagicMock(spec=StructuredLogger),
        time_window="all_time",
        llm_model_name="chatgpt-5.2",
        llm_client=mock_openai_client,
    )


@pytest.fixture
def mock_job() -> MagicMock:
    return MagicMock(
        category="Computing",
        subreddit_list=["Nvidia", "AMD"],
        status=JobStatus.RUNNING,
        started_at=datetime.now(tz=timezone.utc),
        completed_at=None,
        result=None,
        error=None,
    )
