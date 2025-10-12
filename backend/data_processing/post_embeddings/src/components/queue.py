# Bounded Internal Queue to handle buffering unprocessed recieved msgs
# has logic to stop recieving if queue is too full to prevent OOM
from confluent_kafka import Consumer  # type: ignore
from ..middleware.logger import StructuredLogger
import time
from queue import Queue


# Internal Queue to buffer messages polled from kafka and set a hard limit
# for memory management and preventing OOM
def bounded_internal_queue(
    consumer: Consumer,
    internal_queue: Queue,
    high_wm: int,  # 80% of max queue size
    low_wm: int,  # 40% of max queue size
    structured_logger: StructuredLogger,
    running: bool,
) -> None:
    paused = False

    while running:
        if not paused and internal_queue.qsize() >= high_wm:
            consumer.pause()  # stops partition fetch
            paused = True
            structured_logger.info(
                event_type="queue", message="Queue paused due to passing upper bound"
            )
            continue  # skips polling while paused
        elif paused and internal_queue.qsize() <= low_wm:
            consumer.resume()
            paused = False
            structured_logger.info(event_type="queue", message="Queue resumed, below lower bound")

        # Only poll when not paused
        if paused:
            time.sleep(1)
            continue

        msg = consumer.poll(timeout_ms=1000)
        if not msg:  # handling no msgs
            continue

        postID, postMsg, partition, topic, offset = msg
        internal_queue.put(
            {
                "topic": topic,  # need topic and partition in main thread to commit offsets properly
                "partition": partition,
                "offset": offset,
                "postID": postID,
                "postBody": postMsg,
            }
        )

        time.sleep(0.01)
