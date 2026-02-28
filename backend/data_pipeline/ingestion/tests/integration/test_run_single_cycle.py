from unittest.mock import MagicMock
from datetime import datetime
from datetime import timezone
from data_pipeline_utils.job_state_manager import JobState
from data_pipeline_utils.run_single_cycle import run_single_cycle
from src.ingestion_service import IngestionService
from src.api.schemas import JobStatus
from src.api.schemas import CurrentJob
from src.api.schemas import IngestionResult
from unittest.mock import patch

job_state = JobState()

def test_successful_run_updates_job_state(create_ingestion_service: IngestionService) -> None:
    """Successful run_single_cycle should complete job with result"""
    current_job = CurrentJob(
        category="Computing",
        subreddit_list=["GPU"],
        status=JobStatus.RUNNING,
        started_at=datetime.now(tz=timezone.utc),
    )
    job_state.set_running_job(current_job)

    mock_result = IngestionResult(
        posts_processed=10, comments_processed=50, comments_inserted=30, cancelled=False
    )

    with patch.object(create_ingestion_service, "run_ingestion_pipeline", return_value=mock_result):
        run_single_cycle(job_state, "ingestion_service", create_ingestion_service.run_ingestion_pipeline, create_ingestion_service.logger)

        current_job = job_state.get_current_job()
        assert current_job is not None
        assert current_job.status == JobStatus.COMPLETED
        assert current_job.result == mock_result
        assert current_job.completed_at is not None
        assert current_job.error is None


def test_exception_in_pipeline_fails_job(create_ingestion_service: IngestionService, mock_job: MagicMock) -> None:
    """Exception in pipeline should fail job with error message"""
    job_state.set_running_job(mock_job)

    error_msg = "Database connection timeout"

    with patch.object(
        create_ingestion_service, "run_ingestion_pipeline", side_effect=Exception(error_msg)
    ):
        run_single_cycle(job_state, "ingestion_service", create_ingestion_service.run_ingestion_pipeline, create_ingestion_service.logger)

        current_job = job_state.get_current_job()
        assert current_job is not None
        assert current_job.status == JobStatus.FAILED
        assert current_job.error == error_msg
        assert current_job.completed_at is not None
        assert current_job.result is None


def test_logger_info_called_on_success(create_ingestion_service: IngestionService, mock_job: MagicMock) -> None:
    """Logger should log info message on successful completion"""
    job_state.set_running_job(mock_job)

    mock_result = IngestionResult(
        posts_processed=10, comments_processed=50, comments_inserted=30, cancelled=False
    )

    with patch.object(
        create_ingestion_service, "run_ingestion_pipeline", return_value=mock_result
    ):
        with patch.object(create_ingestion_service.logger, "info") as mock_logger_info:
            run_single_cycle(job_state, "ingestion_service", create_ingestion_service.run_ingestion_pipeline, create_ingestion_service.logger)

            mock_logger_info.assert_called_once()
            call_kwargs = mock_logger_info.call_args[1]
            assert call_kwargs["event_type"] == "ingestion_service run"
            assert "completed" in call_kwargs["message"].lower()
            assert str(mock_result.posts_processed) in call_kwargs["message"]
            assert str(mock_result.comments_inserted) in call_kwargs["message"]


def test_zero_results_completes_successfully(create_ingestion_service: IngestionService, mock_job: MagicMock) -> None:
    """Pipeline with zero results should still complete successfully"""
    job_state.set_running_job(mock_job)

    mock_result = IngestionResult(
        posts_processed=0, comments_processed=0, comments_inserted=0, cancelled=False
    )

    with patch.object(
        create_ingestion_service, "run_ingestion_pipeline", return_value=mock_result
    ):
        run_single_cycle(job_state, "ingestion_service", create_ingestion_service.run_ingestion_pipeline, create_ingestion_service.logger)

        current_job = job_state.get_current_job()
        assert current_job is not None
        assert current_job.status == JobStatus.COMPLETED
        assert current_job.result == mock_result


def test_multiple_exception_types_all_handled(create_ingestion_service: IngestionService, mock_job: MagicMock) -> None:
    """All exception types should be caught and handled consistently"""
    exception_types = [
        ValueError("Invalid parameter"),
        TypeError("Type error"),
        RuntimeError("Runtime error"),
        KeyError("Missing key"),
        ConnectionError("Connection failed"),
    ]

    for exception in exception_types:
        job_state.set_running_job(mock_job)

        with patch.object(
            create_ingestion_service, "run_ingestion_pipeline", side_effect=exception
        ):
            run_single_cycle(job_state, "ingestion_service", create_ingestion_service.run_ingestion_pipeline, create_ingestion_service.logger)

            current_job = job_state.get_current_job()
            assert current_job is not None
            assert current_job.status == JobStatus.FAILED
            assert current_job.error == str(exception)
