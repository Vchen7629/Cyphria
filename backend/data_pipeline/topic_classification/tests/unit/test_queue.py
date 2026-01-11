import pytest
from queue import Queue
from threading import Thread
import time
from unittest.mock import MagicMock

from src.components.queue import bounded_internal_queue
from src.middleware.logger import StructuredLogger


@pytest.fixture
def mock_consumer():
    consumer = MagicMock()
    consumer.pause = MagicMock()
    consumer.resume = MagicMock()
    return consumer


def test_adaptive_queue_flow(mock_consumer):
    # Small queue for testing
    q = Queue(maxsize=5)
    logger = StructuredLogger(pod="test")

    # Prepare controlled messages
    messages = [
        ("id1", "msg1", 0, "raw-data", 0),
        ("id2", "msg2", 0, "raw-data", 1),
        ("id3", "msg3", 0, "raw-data", 2),
        ("id4", "msg4", 0, "raw-data", 3),
    ]

    # Create a generator to simulate poll
    def poll_side_effect(timeout_ms):
        if messages:
            return messages.pop(0)
        return None  # no more messages

    mock_consumer.poll = MagicMock(side_effect=poll_side_effect)

    # Run bounded_internal_queue in a thread
    running = True
    thread = Thread(
        target=bounded_internal_queue, args=(mock_consumer, q, 4, 2, logger, running), daemon=True
    )
    thread.start()

    # Wait for the queue to fill high watermark and trigger pause
    time.sleep(0.2)  # short sleep since queue is tiny and messages are few
    assert mock_consumer.pause.called, "Queue never paused when hitting high watermark"

    # Remove two items to drop below low watermark
    q.get()
    q.get()

    # Give thread time to detect low watermark and resume
    time.sleep(0.2)
    assert mock_consumer.resume.called, "Queue never resumed when dropping below low watermark"

    # Stop the thread
    running = False
