from datetime import datetime
from datetime import timezone
from src.api.schemas import JobStatus
from src.api.job_state import JobState
import pytest


def tests_marks_running_job_failed() -> None:
    """Calling fail job when a running job is active should mark it as failed"""
    job_state = JobState()
    before = datetime.now(tz=timezone.utc)
    job_state.create_job(category="Computing", subreddit_list=["Nvidia", "AMD"])
    job_state.fail_job(error="some error")
    after = datetime.now(tz=timezone.utc)

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.status == JobStatus.FAILED
    assert current_job.error == "some error"
    assert current_job.completed_at is not None
    assert before <= current_job.completed_at <= after


@pytest.mark.parametrize(argnames="error", argvalues=[None, "", "  "])
def test_invalid_error_params(error: str | None) -> None:
    """ValueError should be raised if the error input param is invalid (None, empty string, whitespace)"""
    job_state = JobState()

    with pytest.raises(ValueError, match="Missing error"):
        job_state.fail_job(error)  # type: ignore


def test_valid_whitespace() -> None:
    """If error is a string with whitespace, it should still work"""
    job_state = JobState()
    before = datetime.now(tz=timezone.utc)
    job_state.create_job(category="Computing", subreddit_list=["Nvidia", "AMD"])
    job_state.fail_job(error="some error")
    after = datetime.now(tz=timezone.utc)

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.status == JobStatus.FAILED
    assert current_job.error == "some error"
    assert current_job.completed_at is not None
    assert before <= current_job.completed_at <= after
