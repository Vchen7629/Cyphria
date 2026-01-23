# Track current run state
from typing import Any
from src.worker import LLMSummaryWorker
import signal

class RunState:
    """Mutable container"""
    current_service: LLMSummaryWorker | None = None
    run_in_progress = False

run_state = RunState()

def signal_handler(signum: int, _frame: Any) -> None:
    """
    Signal handler for graceful shutdown during an active run.
    Sets cancel_requested on the running service so it stops at the next checkpoint.
    """
    signal_name = signal.Signals(signum).name
    if run_state.current_service is not None:
        # Log via app state logger if available
        print(f"Received {signal_name}, requesting graceful cancellation...")
        run_state.current_service.cancel_requested = True

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
