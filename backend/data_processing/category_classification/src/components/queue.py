from confluent_kafka import Consumer  # type: ignore
from queue import Queue
from ..middleware.logger import StructuredLogger
import time


def bounded_internal_queue(
    consumer: Consumer,
    internal_queue: Queue,
    high_wm: int,
    low_wm: int,
    structured_logger: StructuredLogger,
    running: bool,
):
    paused = False

    while running:
        # pause it if our items in the queue exceeds our upper limit
        if not paused and internal_queue.qsize() >= high_wm:
            consumer.pause()  # stops fetching new msgs from kafka part
            paused = True
            structured_logger.info(
                event_type="queue", message="Queue paused due to passing upper bound"
            )
            continue  # skips polling while paused
        # resume fetching items into this queue if we processed items back
        # down to a safe level
        elif paused and internal_queue.qsize() <= low_wm:
            consumer.resume()
            paused = False
            structured_logger.info(event_type="queue", message="Queue resumed, below lower bound")

        # Only poll when not paused
        if paused:
            time.sleep(1)
            continue

        msg = consumer.poll(timeout_ms=1000)
        if not msg:
            continue

        postID, embeddings, partition, topic, offset = msg
        internal_queue.put(
            {
                "topic": topic,
                "partition": partition,
                "offset": offset,
                "postID": postID,
                "embeddings": embeddings,
            }
        )

        time.sleep(0.01)
