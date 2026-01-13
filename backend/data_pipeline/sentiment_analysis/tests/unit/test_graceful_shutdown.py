from src.worker import StartService
from unittest.mock import patch, MagicMock
import signal

def test_shutdown_signal_stops_processing_loop() -> None:
    """Shutdown signal should properly set shutdown requested flag"""
    with patch.object(StartService, '_database_conn_lifespan'), \
         patch.object(StartService, '_initialize_absa_model'):
        service = StartService()

        assert service.shutdown_requested is False

        service._signal_handler(signal.SIGTERM, None)

        assert service.shutdown_requested is True
        