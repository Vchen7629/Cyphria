from datetime import datetime
from datetime import timezone
from src.api.schemas import JobStatus
from src.api.job_state import JobState
import pytest

def test_correct_values_set() -> None:
    """Category, status, and started_at should be correctly set in the self._current_job value"""
    job_state = JobState()
    before = datetime.now(tz=timezone.utc)
    job_state.create_job(category="GPU")
    after = datetime.now(tz=timezone.utc)

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.category == "GPU"
    assert current_job.status == JobStatus.RUNNING
    assert before <= current_job.started_at <= after

def test_optional_fields_initialized_to_none() -> None:
    """Creat job should set completed at, result and error to None"""
    job_state = JobState()
    job_state.create_job(category="GPU")

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.completed_at is None
    assert current_job.result is None
    assert current_job.error is None

def test_none_category_raises_error() -> None:
    """ValueError should be raised for None category"""
    job_state = JobState()

    with pytest.raises(ValueError, match="category cannot be None or empty string"):
        job_state.create_job(category=None) # type: ignore

def test_empty_string_category_raises_error() -> None:
    """ValueError should be raised for category with empty string"""
    job_state = JobState()

    with pytest.raises(ValueError, match="category cannot be None or empty string"):
        job_state.create_job(category="")

def test_whitespace_only_category_raises_error() -> None:
    """ValueError should be raised for whitespace-only category"""
    job_state = JobState()

    with pytest.raises(ValueError, match="category cannot be None or empty string"):
        job_state.create_job(category="   ")

def test_category_with_whitespace() -> None:
    """Category string with whitespace should be valid"""
    job_state = JobState()
    job_state.create_job(category="  GPU  ")

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.category == "  GPU  "

