from src.api.job_state import JobState

def test_check_running_job() -> None:
    """Calling is_running while a job is running should return True"""
    job_state = JobState()
    job_state.create_job(product_topic="GPU")

    assert job_state.is_running() == True

def test_check_not_running_job() -> None:
    """Calling is_running while a job is not running should return False"""
    job_state = JobState()
    assert job_state.is_running() == False

