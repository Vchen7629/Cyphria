
from typing import Any
from typing import Generic
from typing import TypeVar
from typing import Optional
from threading import Lock
from datetime import datetime
from datetime import timezone
from pipeline_types.data_pipeline import JobStatus

TJob = TypeVar("TJob")

class JobState(Generic[TJob]):
    def __init__(self) -> None:
        self._current_job: Optional[TJob] = None
        self._lock = Lock()

    def set_running_job(self, job: TJob) -> None:
        """
        Create a new job

        Args:
            job: The job details
        """
        with self._lock:
            self._current_job = job

    def mark_complete(self, result: Any) -> None:
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

    def mark_failed(self, error: str) -> None:
        """
        Mark job as failed with error

        Args:
            error: the error type

        Raises:
            ValueError: if error is None or empty string
        """
        if not error or not error.strip():
            raise ValueError("Missing error type")

        with self._lock:
            if self._current_job:
                self._current_job.status = JobStatus.FAILED
                self._current_job.error = error
                self._current_job.completed_at = datetime.now(tz=timezone.utc)

    def get_current_job(self) -> Optional[TJob]:
        """Get currently running job's state"""
        with self._lock:
            return self._current_job

    def is_running(self) -> bool:
        """Check if any job is currently running"""
        with self._lock:
            return self._current_job is not None and self._current_job.status == JobStatus.RUNNING
