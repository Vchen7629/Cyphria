from threading import Lock
from typing import Optional
from datetime import datetime
from datetime import timezone
from src.api.schemas import CurrentJob
from src.api.schemas import RankingResult
from src.api.schemas import JobStatus

class JobState:
    """Thread-safe state for the single current job, state tracks job metadata"""
    def __init__(self) -> None:
        self._current_job: Optional[CurrentJob] = None
        self._lock = Lock()

    def create_job(self, product_topic: str) -> None:
        """
        Create a new job

        Args:
            product_topic: topic of products we are ranking

        Raises:
            ValueError: if product_topic is None or empty string
        """
        if not product_topic or product_topic.strip() == "":
            raise ValueError("product_topic cannot be None or empty string")

        with self._lock:
            self._current_job = CurrentJob(
                product_topic=product_topic,
                status=JobStatus.RUNNING,
                started_at=datetime.now(tz=timezone.utc)
            )
    
    def complete_job(self, result: RankingResult) -> None:
        """
        Mark job as done with the result metadata

        Args:
            result: the result metadata
        
        Raises:
            ValueError: if result is None
        """
        if not result:
            raise ValueError("No Ranking result provided")

        with self._lock:
            if self._current_job:
                self._current_job.status = JobStatus.CANCELLED if result.cancelled else JobStatus.COMPLETED
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
        if not error or error.strip() == "":
            raise ValueError("Error cannot be None or empty string")
            
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