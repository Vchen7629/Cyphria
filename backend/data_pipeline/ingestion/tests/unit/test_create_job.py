from typing import Optional
from datetime import datetime
from datetime import timezone
from src.api.schemas import JobStatus
from src.api.job_state import JobState
import pytest


def test_correct_values_set() -> None:
    """product_topic, status, and started_at should be correctly set in the self._current_job value"""
    job_state = JobState()
    before = datetime.now(tz=timezone.utc)
    job_state.create_job(category="Computing", subreddit_list=["Nvidia", "AMD"])
    after = datetime.now(tz=timezone.utc)

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.category == "Computing"
    assert current_job.subreddit_list == ["Nvidia", "AMD"]
    assert current_job.status == JobStatus.RUNNING
    assert before <= current_job.started_at <= after


def test_optional_fields_initialized_to_none() -> None:
    """Create job should set completed at, result and error to None"""
    job_state = JobState()
    job_state.create_job(category="Computing", subreddit_list=["Nvidia", "AMD"])

    current_job = job_state.get_current_job()
    assert current_job is not None
    assert current_job.completed_at is None
    assert current_job.result is None
    assert current_job.error is None


@pytest.mark.parametrize(
    argnames="category,subreddit_list",
    argvalues=[
        # category tests
        (None, ["Nvidia", "AMD"]),
        ("", ["Nvidia", "AMD"]),
        ("  ", ["Nvidia", "AMD"]),
        # subreddit_list tests
        ("Computing", None),
        ("Computing", []),
    ],
)
def test_invalid_input_params_raises_error(
    category: Optional[str], subreddit_list: Optional[list[str]]
) -> None:
    """ValueError should be raised for None category"""
    job_state = JobState()

    if not category or category.strip() == "":
        with pytest.raises(ValueError, match="Missing category"):
            job_state.create_job(category, subreddit_list)  # type: ignore
    else:
        with pytest.raises(ValueError, match="Missing subreddit_list"):
            job_state.create_job(category, subreddit_list)  # type: ignore
