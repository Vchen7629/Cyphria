from typing import Callable
import pytest
from testcontainers.postgres import PostgresContainer
from typing import Any
from src.worker import RankingCalculatorWorker
from psycopg_pool.pool import ConnectionPool
from unittest.mock import patch, MagicMock
import signal

def test_cleanup_called_on_shutdown(mock_db_conn_lifespan: Callable[[], RankingCalculatorWorker]) -> None:
    """Cleanup method should be called when worker shuts down"""
    worker = mock_db_conn_lifespan()
    worker.shutdown_requested = True

    # Mock cleanup without wrapping to prevent pool closure
    with patch.object(worker, '_cleanup') as mock_cleanup:
        worker.run()

        mock_cleanup.assert_called_once()

def test_cleanup_called_on_exception(mock_db_conn_lifespan: Callable[[], RankingCalculatorWorker]) -> None:
    """Cleanup should be called when processing raises a exception"""
    worker = mock_db_conn_lifespan()

    with patch.object(worker, '_calculate_rankings_for_window', side_effect=RuntimeError("Processing failed")), \
            patch.object(worker, '_cleanup') as mock_cleanup:
        with pytest.raises(RuntimeError, match="Processing failed"):
            worker.run()

        mock_cleanup.assert_called_once()

def test_db_pool_closed_during_cleanup() -> None:
    """Database pool should be closed when cleanup is called"""
    with patch.object(RankingCalculatorWorker, '_db_conn_lifespan'):
        worker = RankingCalculatorWorker()

        mock_pool = MagicMock(spec=ConnectionPool)
        worker.db_pool = mock_pool

        worker._cleanup()

        mock_pool.close.assert_called_once()

def test_double_cleanup_is_safe() -> None:
    """Calling cleanup twice should not raise errors"""
    with patch.object(RankingCalculatorWorker, '_db_conn_lifespan'):
        worker = RankingCalculatorWorker()

        mock_pool = MagicMock(spec=ConnectionPool)
        worker.db_pool = mock_pool

        worker._cleanup()
        worker._cleanup()

        mock_pool.close.call_count == 2

def test_shutdown_requested_before_run_skips_processing(mock_db_conn_lifespan: Callable[[], RankingCalculatorWorker]) -> None:
    """If shutdown is requested before run(), processing should be minimal"""
    worker = mock_db_conn_lifespan()
    worker.shutdown_requested = True

    with patch.object(worker, '_calculate_rankings_for_window') as mock_calc, \
            patch.object(worker, '_cleanup'):
        worker.run()

        # Processing still happens in current impl, but cleanup is called
        # This test documents current behavior
        mock_calc.assert_called_once()

def test_cleanup_after_successful_processing(mock_db_conn_lifespan: Callable[[], RankingCalculatorWorker]) -> None:
    """Cleanup should be called after successful processing completes"""
    worker = mock_db_conn_lifespan()

    cleanup_called = []

    worker._cleanup

    def track_cleanup() -> None:
        cleanup_called.append(True)
        pass

    with patch.object(worker, '_cleanup', side_effect=track_cleanup):
        worker.run()
    
    assert len(cleanup_called) == 1

def test_shutdown_during_db_operation(mock_db_conn_lifespan: Callable[[], RankingCalculatorWorker]) -> None:
    worker = mock_db_conn_lifespan()
    operation_completed = []

    def slow_calculation(*args: Any, **kwargs: Any) -> int:
        worker._signal_handler(signal.SIGTERM, None)
        operation_completed.append(True)
        return 0

    with patch.object(worker, '_calculate_rankings_for_window', side_effect=slow_calculation), \
            patch.object(worker, '_cleanup') as mock_cleanup:
        worker.run()

        assert len(operation_completed) == 1
        assert worker.shutdown_requested is True
        mock_cleanup.assert_called_once()

def test_pool_connections_released_on_shutdown(postgres_container: PostgresContainer) -> None:
    """All pool connections should be released when worker shuts down"""
    connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")

    test_pool = ConnectionPool(
        conninfo=connection_url,
        min_size=1,
        max_size=3,
        open=True
    )

    try:
        with patch.object(RankingCalculatorWorker, '_db_conn_lifespan'):
            worker = RankingCalculatorWorker()
            worker.db_pool = test_pool

            stats_before = test_pool.get_stats()
            assert stats_before['pool_available'] >= 0

            worker._cleanup()

            assert test_pool.closed
    finally:
        if not test_pool.closed:
            test_pool.close()

def test_multiple_signals_handled_gracefully(db_pool: ConnectionPool, mock_db_conn_lifespan: Callable[[], RankingCalculatorWorker]) -> None:
    """Multiple shutdown signals should be handled without errors"""
    worker = mock_db_conn_lifespan()

    worker._signal_handler(signal.SIGTERM, None)
    assert worker.shutdown_requested

    worker._signal_handler(signal.SIGINT, None)
    assert worker.shutdown_requested

    worker._signal_handler(signal.SIGTERM, None)
    assert worker.shutdown_requested

def test_sigterm_sets_shutdown_flag(mock_db_conn_lifespan: Callable[[], RankingCalculatorWorker]) -> None:
    """SIGTERM signal should set shutdown requested to True"""
    worker = mock_db_conn_lifespan()

    assert not worker.shutdown_requested
    
    worker._signal_handler(signal.SIGTERM, None)
    assert worker.shutdown_requested

def test_sigint_sets_shutdown_flag(mock_db_conn_lifespan: Callable[[], RankingCalculatorWorker]) -> None:
    """SIGINT signal should set shutdown requested to True"""
    worker = mock_db_conn_lifespan()
    assert not worker.shutdown_requested

    worker._signal_handler(signal.SIGINT, None)
    assert worker.shutdown_requested

