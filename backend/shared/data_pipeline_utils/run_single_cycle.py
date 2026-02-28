from shared_core.logger import StructuredLogger
from typing import Any
from data_pipeline_utils.job_state_manager import JobState

def run_single_cycle(
    job_state: JobState, 
    service_name: str,
    processing_pipeline: Any,
    logger: StructuredLogger
) -> None:
    """
    Run one complete processing cycle and update job state
    runs in a background thread and handles all errors internally 
    and updates the job state

    Args:
        job_state: JobState instance to update with progress/results

    Raise:
        Value error if not job state
    """
    if not job_state:
        raise ValueError("Job state must be provided for the run single cycle")

    event_type = f"{service_name} run"

    try:
        result = processing_pipeline()

        job_state.mark_complete(result)

        logger.info(
            event_type=event_type,
            message=f"Ingestion completed: {result.posts_processed} posts, {result.comments_inserted} comments processed",
        )

    except Exception as e:
        logger.error(
            event_type=event_type, message=f"Ingestion failed: {str(e)}"
        )
        job_state.mark_failed(str(e))