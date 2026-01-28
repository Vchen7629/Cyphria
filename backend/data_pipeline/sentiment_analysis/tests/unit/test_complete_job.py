from datetime import datetime
from datetime import timezone
from src.api.schemas import JobStatus
from src.api.job_state import JobState
from src.api.schemas import SentimentResult
import pytest


def tests_marks_complete_running_job_complete() -> None:
    """Calling complete job when a running job is active should mark it as done"""
    job_state = JobState()
    before = datetime.now(tz=timezone.utc)
    job_state.create_job(product_topic="GPU")

    mock_result = SentimentResult(comments_inserted=10, comments_updated=10, cancelled=False)

    job_state.complete_job(mock_result)
    after = datetime.now(tz=timezone.utc)
    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.status == JobStatus.COMPLETED
    assert current_job.result == mock_result
    assert current_job.completed_at is not None
    assert before <= current_job.completed_at <= after


def tests_marks_cancelled_running_job_complete() -> None:
    """Calling cancelled job when a running job is active should mark it as done"""
    job_state = JobState()
    before = datetime.now(tz=timezone.utc)
    job_state.create_job(product_topic="GPU")

    mock_result = SentimentResult(comments_inserted=10, comments_updated=10, cancelled=True)

    job_state.complete_job(mock_result)
    after = datetime.now(tz=timezone.utc)

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.status == JobStatus.CANCELLED
    assert current_job.result == mock_result
    assert current_job.completed_at is not None
    assert before <= current_job.completed_at <= after


def test_missing_ingestion_result() -> None:
    """ValueError should be raised if no ranking result is provided"""
    job_state = JobState()

    with pytest.raises(ValueError, match="No Ranking result provided"):
        job_state.complete_job(result=None)  # type: ignore
