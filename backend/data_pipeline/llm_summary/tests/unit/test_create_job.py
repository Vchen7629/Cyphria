from datetime import datetime
from datetime import timezone
from src.api.schemas import JobStatus
from src.api.job_state import JobState
import pytest

def test_correct_values_set() -> None:
    """time_window, status, and started_at should be correctly set in the self._current_job value"""
    job_state = JobState()
    before = datetime.now(tz=timezone.utc)
    job_state.create_job(time_window="all_time")
    after = datetime.now(tz=timezone.utc)

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.time_window == "all_time"
    assert current_job.status == JobStatus.RUNNING
    assert before <= current_job.started_at <= after

def test_optional_fields_initialized_to_none() -> None:
    """Creat job should set completed at, result and error to None"""
    job_state = JobState()
    job_state.create_job(time_window="GPU")

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.completed_at is None
    assert current_job.result is None
    assert current_job.error is None

@pytest.mark.parametrize("time_window", [(None), (""), ("  ")])
def test_invalid_category_raises_error(time_window: str | None) -> None:
    """ValueError should be raised for invalid time_window param (None, empty string, white space)"""
    job_state = JobState()

    with pytest.raises(ValueError, match="time_window cannot be None or empty string"):
        job_state.create_job(time_window) # type: ignore

def test_category_with_whitespace() -> None:
    """time window string with whitespace should be valid"""
    job_state = JobState()
    job_state.create_job(time_window="  all_time  ")

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.time_window == "  all_time  "

