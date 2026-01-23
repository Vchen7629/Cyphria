from unittest.mock import MagicMock
from src.api.signal_handler import run_state, signal_handler
import signal

def test_signal_handler_doesnt_error_when_no_service() -> None:
    """Signal handler should be safe when no service is running"""
    run_state.current_service = None

    signal_handler(signal.SIGTERM, None)
    signal_handler(signal.SIGINT, None)

def test_signal_handler_sets_cancel_flag() -> None:
    """SIGTERM/SIGINT should set cancel_requested on running service"""
    mock_service = MagicMock()
    mock_service.cancel_requested = False

    run_state.current_service = mock_service

    try:
        signal_handler(signal.SIGTERM, None)

        assert mock_service.cancel_requested
    finally:
        run_state.current_service is None

def test_multiple_signal_handler_sets_cancel_flag() -> None:
    """Multiple SIGTERM/SIGINT shouldnt set cancel_requested back to False"""
    mock_service = MagicMock()
    mock_service.cancel_requested = False

    run_state.current_service = mock_service

    try:
        signal_handler(signal.SIGTERM, None)
        assert mock_service.cancel_requested

        # second signal handler call shouldnt set it back to false
        signal_handler(signal.SIGINT, None)
        assert mock_service.cancel_requested

    finally:
        run_state.current_service is None