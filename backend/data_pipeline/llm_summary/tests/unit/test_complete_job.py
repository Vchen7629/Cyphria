from datetime import datetime
from datetime import timezone
from src.api.schemas import JobStatus
from src.api.job_state import JobState
from src.api.schemas import SummaryResult
import pytest


def tests_marks_complete_running_job_complete() -> None:
    """Calling complete job when a running job is active should mark it as done"""
    job_state = JobState()
    before = datetime.now(tz=timezone.utc)
    job_state.create_job(time_window="all_time")

    mock_result = SummaryResult(products_summarized=10, cancelled=False)

    job_state.complete_job(mock_result)
    after = datetime.now(tz=timezone.utc)
    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.status == JobStatus.COMPLETED
    assert current_job.result == mock_result
    assert current_job.completed_at is not None
    assert before <= current_job.completed_at <= after


def test_missing_ingestion_result() -> None:
    """ValueError should be raised if no ranking result is provided"""
    job_state = JobState()

    with pytest.raises(ValueError, match="No Ranking result provided"):
        job_state.complete_job(result=None)  # type: ignore
