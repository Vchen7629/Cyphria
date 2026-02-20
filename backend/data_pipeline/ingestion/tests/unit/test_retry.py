from unittest.mock import Mock, patch
from src.db_utils.retry import retry_with_backoff
import pytest
import psycopg


def test_retry_succeeds_after_transient_error() -> None:
    """Test that function retries and succeeds after transient errors."""
    mock_func = Mock(
        side_effect=[
            psycopg.OperationalError("Connection lost"),
            psycopg.OperationalError("Connection lost again"),
            "success",
        ]
    )

    @retry_with_backoff(max_retries=3, initial_delay=0.1)
    def test_func() -> Mock:
        return mock_func()

    result = test_func()

    assert result == "success"
    assert mock_func.call_count == 3


def test_retry_fails_after_max_retries() -> None:
    """Test that function fails after exhausting all retry attempts."""
    mock_func = Mock(side_effect=psycopg.OperationalError("Connection lost"))

    @retry_with_backoff(max_retries=2, initial_delay=0.1)
    def test_func() -> Mock:
        return mock_func()

    with pytest.raises(psycopg.OperationalError):
        test_func()

    assert mock_func.call_count == 3  # 1 initial + 2 retries


def test_non_retryable_error_fails_immediately() -> None:
    """Test that non-retryable errors fail immediately without retry."""
    mock_func = Mock(side_effect=psycopg.errors.NotNullViolation("Missing required field"))

    @retry_with_backoff(max_retries=3, initial_delay=0.1)
    def test_func() -> Mock:
        return mock_func()

    with pytest.raises(psycopg.errors.NotNullViolation):
        test_func()

    assert mock_func.call_count == 1


def test_exponential_backoff_timing() -> None:
    """Test that delays follow exponential backoff pattern and respect max_delay."""
    mock_func = Mock(
        side_effect=[
            psycopg.OperationalError("Error"),
            psycopg.OperationalError("Error"),
            psycopg.OperationalError("Error"),
            "success",
        ]
    )

    @retry_with_backoff(max_retries=4, initial_delay=1.0, max_delay=5.0, backoff_multiplier=2.0)
    def test_func() -> Mock:
        return mock_func()

    with patch("time.sleep") as mock_sleep:
        result = test_func()

    assert result == "success"
    # Delays: 1.0, 2.0, 4.0
    assert mock_sleep.call_count == 3
    assert mock_sleep.call_args_list[0][0][0] == 1.0
    assert mock_sleep.call_args_list[1][0][0] == 2.0
    assert mock_sleep.call_args_list[2][0][0] == 4.0


def test_logger_called_on_final_failure() -> None:
    """Test that logger is called only on final failure after all retries exhausted."""
    mock_logger = Mock()
    mock_func = Mock(side_effect=psycopg.errors.DeadlockDetected("Deadlock"))

    @retry_with_backoff(max_retries=2, initial_delay=0.1, logger=mock_logger)
    def test_func() -> Mock:
        return mock_func()

    with pytest.raises(psycopg.errors.DeadlockDetected):
        test_func()

    assert mock_logger.error.call_count == 1
    call_args = mock_logger.error.call_args[1]
    assert call_args["event_type"] == "Database Retry"
    assert "failed after 2 retries" in call_args["message"]
    assert call_args["error_type"] == "DeadlockDetected"
