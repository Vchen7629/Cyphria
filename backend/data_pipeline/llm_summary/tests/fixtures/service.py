from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
import pytest
import os
os.environ.setdefault("PRODUCT_CATEGORY", "GPU")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASS", "test_pass")
from src.core.logger import StructuredLogger
from src.summary_service import LLMSummaryService

@pytest.fixture
def create_llm_summary_service(db_pool: ConnectionPool, mock_openai_client: MagicMock) -> LLMSummaryService:
    """Creates a llm_summary service Instance fixture"""
    return LLMSummaryService(
        logger=StructuredLogger(pod="sentiment_analysis"),
        time_window="all_time",
        db_pool=db_pool,
        llm_model_name="gpt-5.2",
        llm_client=mock_openai_client
    )

@pytest.fixture
def mock_summary_service(mock_openai_client: MagicMock) -> LLMSummaryService:
    """Mock summary service with all dependencies mocked for use in unit tests"""
    return LLMSummaryService(
        db_pool=MagicMock(spec=ConnectionPool),
        logger=MagicMock(spec=StructuredLogger),
        time_window="all_time",
        llm_model_name="chatgpt-5.2",
        llm_client=mock_openai_client
    )