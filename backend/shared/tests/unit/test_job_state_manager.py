from unittest.mock import MagicMock
from datetime import datetime
from datetime import timezone
from pipeline_types.data_pipeline import JobStatus
from data_pipeline_utils.job_state_manager import JobState
import pytest

job_state = JobState()

def test_set_running_job_initialized_to_none() -> None:
    """_set_running_job should store the job with completed_at, result and error as None"""
    mock_job = MagicMock(completed_at=None, result=None, error=None)
    job_state.set_running_job(mock_job)

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.completed_at is None
    assert current_job.result is None
    assert current_job.error is None

def test_set_running_job_correct_values_set(mock_job: MagicMock) -> None:
    """set_running_job should store the job with the values it was given"""
    job_state.set_running_job(mock_job)

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.category == "Computing"
    assert current_job.subreddit_list == ["Nvidia", "AMD"]
    assert current_job.status == JobStatus.RUNNING

def test_mark_fail_current_job(mock_job: MagicMock) -> None:
    """It should mark the current job as Failed"""
    before = datetime.now(tz=timezone.utc)
    job_state.set_running_job(mock_job)
    job_state.mark_failed(error="some error")
    after = datetime.now(tz=timezone.utc)

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.status == JobStatus.FAILED
    assert current_job.error == "some error"
    assert current_job.completed_at is not None
    assert before <= current_job.completed_at <= after

def test_check_running_job(mock_job: MagicMock) -> None:
    """Calling is_running while a job is running should return True"""
    job_state.set_running_job(mock_job)

    assert job_state.is_running()

def test_check_not_running_job() -> None:
    """Calling is_running while a job is not running should return False"""
    job_state = JobState()
    assert not job_state.is_running()

@pytest.mark.parametrize(argnames="error", argvalues=[None, "", "  "])
def test_mark_fail_invalid_parameter(error: str | None) -> None:
    """ValueError should be raised if the error input param is invalid (None, empty string, whitespace)"""
    with pytest.raises(ValueError, match="Missing error"):
        job_state.mark_failed(error)  # type: ignore


def test_mark_complete_invalid_parameter() -> None:
    """ValueError should be raised if no ingestion result is provided"""
    with pytest.raises(ValueError, match="No Ingestion result provided"):
        job_state.mark_complete(result=None)  # type: ignore
