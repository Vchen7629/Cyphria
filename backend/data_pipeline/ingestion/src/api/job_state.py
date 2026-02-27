from src.utils.validation import validate_string
from src.utils.validation import validate_list
from threading import Lock
from typing import Optional
from datetime import datetime
from datetime import timezone
from src.api.schemas import CurrentJob, IngestionResult, JobStatus


class JobState:
    """Thread-safe state for the single current job, state tracks job metadata"""

    def __init__(self) -> None:
        self._current_job: Optional[CurrentJob] = None
        self._lock = Lock()

    def create_job(self, category: str, subreddit_list: list[str]) -> None:
        """
        Create a new job

        Args:
            category: the current category we are processing for
            subreddit_list: list of subreddits to fetch and process comments from

        Raises:
            ValueError: if subreddit_list or category is none or category is an empty string
        """
        validate_string(category, "category", raise_http=False)
        validate_list(subreddit_list, "subreddit_list", raise_http=False)

        with self._lock:
            self._current_job = CurrentJob(
                category=category,
                subreddit_list=subreddit_list,
                status=JobStatus.RUNNING,
                started_at=datetime.now(tz=timezone.utc),
            )

    def complete_job(self, result: IngestionResult) -> None:
        """
        Mark job as done with the result metadata

        Args:
            result: the result metadata

        Raises:
            ValueError: if result is None
        """
        if not result:
            raise ValueError("No Ingestion result provided")

        with self._lock:
            if self._current_job:
                self._current_job.status = JobStatus.COMPLETED
                self._current_job.result = result
                self._current_job.completed_at = datetime.now(tz=timezone.utc)

    def fail_job(self, error: str) -> None:
        """
        Mark job as failed with error

        Args:
            error: the error type

        Raises:
            ValueError: if error is None or empty string
        """
        validate_string(error, "error", raise_http=False)

        with self._lock:
            if self._current_job:
                self._current_job.status = JobStatus.FAILED
                self._current_job.error = error
                self._current_job.completed_at = datetime.now(tz=timezone.utc)

    def get_current_job(self) -> Optional[CurrentJob]:
        """Get currently running job's state"""
        with self._lock:
            return self._current_job

    def is_running(self) -> bool:
        """Check if any job is currently running"""
        with self._lock:
            return self._current_job is not None and self._current_job.status == JobStatus.RUNNING
