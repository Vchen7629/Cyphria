from src.api.job_state import JobState

def test_check_running_job() -> None:
    """Calling is_running while a job is running should return True"""
    job_state = JobState()
    job_state.create_job(time_window="all_time")

    assert job_state.is_running()

def test_check_not_running_job() -> None:
    """Calling is_running while a job is not running should return False"""
    job_state = JobState()
    assert not job_state.is_running()

