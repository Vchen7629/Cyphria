from unittest.mock import MagicMock
from datetime import datetime, timezone
from pipeline_types.data_pipeline import JobStatus
import pytest

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