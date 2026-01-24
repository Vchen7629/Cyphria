from datetime import datetime
from datetime import timezone
from src.api.schemas import JobStatus
from src.api.job_state import JobState
import pytest

def test_correct_values_set() -> None:
    """product_topic, status, and started_at should be correctly set in the self._current_job value"""
    job_state = JobState()
    before = datetime.now(tz=timezone.utc)
    job_state.create_job(product_topic="GPU")
    after = datetime.now(tz=timezone.utc)

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.product_topic == "GPU"
    assert current_job.status == JobStatus.RUNNING
    assert before <= current_job.started_at <= after

def test_optional_fields_initialized_to_none() -> None:
    """Creat job should set completed at, result and error to None"""
    job_state = JobState()
    job_state.create_job(product_topic="GPU")

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.completed_at is None
    assert current_job.result is None
    assert current_job.error is None

def test_none_category_raises_error() -> None:
    """ValueError should be raised for None category"""
    job_state = JobState()

    with pytest.raises(ValueError, match="product topic cannot be None or empty string"):
        job_state.create_job(product_topic=None) # type: ignore

@pytest.mark.parametrize(argnames="product_topic", argvalues=[None, "", "  "])
def test_invalid_category_raises_error(product_topic: str | None) -> None:
    """ValueError should be raised for invalid categories (None, empty string, whitespace)"""
    job_state = JobState()

    with pytest.raises(ValueError, match="product topic cannot be None or empty string"):
        job_state.create_job(product_topic) # type: ignore

def test_category_with_whitespace() -> None:
    """product_topic string with whitespace should be valid"""
    job_state = JobState()
    job_state.create_job(product_topic="  GPU  ")

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.product_topic == "  GPU  "

