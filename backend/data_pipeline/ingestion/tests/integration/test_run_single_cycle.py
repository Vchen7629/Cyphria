from src.api.job_state import JobState
from src.ingestion_service import IngestionService
from src.api.schemas import JobStatus, IngestionResult
from unittest.mock import patch

def test_successful_run_updates_job_state(create_ingestion_service: IngestionService) -> None:
    """Successful run_single_cycle should complete job with result"""
    job_state = JobState()
    job_state.create_job("GPU")

    # Mock pipeline to return a successful result
    mock_result = IngestionResult(
        posts_processed=10,
        comments_processed=50,
        comments_inserted=30,
        cancelled=False
    )

    with patch.object(create_ingestion_service, '_run_ingestion_pipeline', return_value=mock_result):
        with patch('src.api.signal_handler.run_state') as mock_run_state:
            create_ingestion_service.run_single_cycle(job_state)

            # Verify job state updated correctly
            current_job = job_state.get_current_job()
            assert current_job is not None
            assert current_job.status == JobStatus.COMPLETED
            assert current_job.result == mock_result
            assert current_job.completed_at is not None
            assert current_job.error is None

            # Verify run_state cleaned up
            assert not mock_run_state.run_in_progress
            assert mock_run_state.current_service is None

def test_cancelled_run_marks_job_cancelled(create_ingestion_service: IngestionService) -> None:
    """Cancelled run should mark job as CANCELLED in job_state"""
    job_state = JobState()
    job_state.create_job("GPU")

    # Mock pipeline to return cancelled result
    mock_result = IngestionResult(
        posts_processed=5,
        comments_processed=20,
        comments_inserted=10,
        cancelled=True
    )

    with patch.object(create_ingestion_service, '_run_ingestion_pipeline', return_value=mock_result):
        with patch('src.api.signal_handler.run_state') as mock_run_state:
            create_ingestion_service.run_single_cycle(job_state)

            # Verify job marked as cancelled
            current_job = job_state.get_current_job()
            assert current_job is not None
            assert current_job.status == JobStatus.CANCELLED
            assert current_job.result == mock_result
            assert current_job.completed_at is not None

            # Verify run_state cleaned up
            assert not mock_run_state.run_in_progress
            assert mock_run_state.current_service is None


def test_exception_in_pipeline_fails_job(create_ingestion_service: IngestionService) -> None:
    """Exception in pipeline should fail job with error message"""
    job_state = JobState()
    job_state.create_job("GPU")

    error_msg = "Database connection timeout"

    with patch.object(create_ingestion_service, '_run_ingestion_pipeline', side_effect=Exception(error_msg)):
        with patch('src.api.signal_handler.run_state') as mock_run_state:
            create_ingestion_service.run_single_cycle(job_state)

            # Verify job marked as failed with error
            current_job = job_state.get_current_job()
            assert current_job is not None
            assert current_job.status == JobStatus.FAILED
            assert current_job.error == error_msg
            assert current_job.completed_at is not None
            assert current_job.result is None

            # Verify run_state cleaned up even on failure
            assert mock_run_state.run_in_progress is False
            assert mock_run_state.current_service is None

def test_run_state_cleanup_in_finally_block(create_ingestion_service: IngestionService) -> None:
    """run_state should be cleaned up in finally block even on exception"""
    job_state = JobState()
    job_state.create_job("GPU")

    with patch.object(create_ingestion_service, '_run_ingestion_pipeline', side_effect=RuntimeError("Test error")):
        with patch('src.api.signal_handler.run_state') as mock_run_state:
            # Set initial state
            mock_run_state.run_in_progress = True
            mock_run_state.current_service = create_ingestion_service

            create_ingestion_service.run_single_cycle(job_state)

            # Verify cleanup happened in finally block
            assert not mock_run_state.run_in_progress
            assert mock_run_state.current_service is None


def test_logger_info_called_on_success(create_ingestion_service: IngestionService) -> None:
    """Logger should log info message on successful completion"""
    job_state = JobState()
    job_state.create_job("GPU")

    mock_result = IngestionResult(
        posts_processed=10,
        comments_processed=50,
        comments_inserted=30,
        cancelled=False
    )

    with patch.object(create_ingestion_service, '_run_ingestion_pipeline', return_value=mock_result):
        with patch('src.api.signal_handler.run_state'):
            with patch.object(create_ingestion_service.logger, 'info') as mock_logger_info:
                create_ingestion_service.run_single_cycle(job_state)

                # Verify logger.info called with success message
                mock_logger_info.assert_called_once()
                call_kwargs = mock_logger_info.call_args[1]
                assert call_kwargs['event_type'] == "ingestion_service run"
                assert "completed" in call_kwargs['message'].lower()
                assert str(mock_result.posts_processed) in call_kwargs['message']
                assert str(mock_result.comments_inserted) in call_kwargs['message']

def test_zero_results_completes_successfully(create_ingestion_service: IngestionService) -> None:
    """Pipeline with zero results should still complete successfully"""
    job_state = JobState()
    job_state.create_job("GPU")

    mock_result = IngestionResult(
        posts_processed=0,
        comments_processed=0,
        comments_inserted=0,
        cancelled=False
    )

    with patch.object(create_ingestion_service, '_run_ingestion_pipeline', return_value=mock_result):
        with patch('src.api.signal_handler.run_state'):
            create_ingestion_service.run_single_cycle(job_state)

            current_job = job_state.get_current_job()
            assert current_job is not None
            assert current_job.status == JobStatus.COMPLETED
            assert current_job.result == mock_result


def test_multiple_exception_types_all_handled(create_ingestion_service: IngestionService) -> None:
    """All exception types should be caught and handled consistently"""
    exception_types = [
        ValueError("Invalid parameter"),
        TypeError("Type error"),
        RuntimeError("Runtime error"),
        KeyError("Missing key"),
        ConnectionError("Connection failed")
    ]

    for exception in exception_types:
        job_state = JobState()
        job_state.create_job("GPU")

        with patch.object(create_ingestion_service, '_run_ingestion_pipeline', side_effect=exception):
            with patch('src.api.signal_handler.run_state'):
                create_ingestion_service.run_single_cycle(job_state)

                current_job = job_state.get_current_job()
                assert current_job is not None
                assert current_job.status == JobStatus.FAILED
                assert current_job.error == str(exception)