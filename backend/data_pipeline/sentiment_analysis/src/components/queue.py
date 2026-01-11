from confluent_kafka import Consumer  # type: ignore
from src.core.logger import StructuredLogger
from src.core.types import QueueMessage
import time
import json
from queue import Queue

def bounded_internal_queue(
    consumer: Consumer,
    internal_queue: Queue[QueueMessage],
    high_wm: int,  # 80% of max queue size
    low_wm: int,  # 40% of max queue size
    structured_logger: StructuredLogger,
) -> None:
    """
    Internal queue to buffer messages polled from kafka with a hard limit
    Stops polling once messages in the queue reach that amount and starts again
    once messages are processed till a lower bound to prevent OOM 

    Args:
        consumer: Kafka consumer
        internal_queue: queue object holding the messages polled from the kafka topic
        high_wm: upper limit of queue size, pauses polling when the number of unprocessed 
                messages hits this ammount
        low_wm: lower limit of queue size, resumes polling once unprocessed images is less than
                or equal to this amount
        structured_logger: logging instance
    """
    paused = False

    while True:
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

        # Parse postBody JSON to extract metadata
        try:
            post_data = json.loads(postMsg)
            subreddit = post_data.get("subreddit", "")
            timestamp = post_data.get("timestamp", "")
            score = post_data.get("score", 0)
            author = post_data.get("author", "")
        except json.JSONDecodeError:
            # If JSON parsing fails, use default values
            structured_logger.error(
                event_type="queue",
                message=f"Failed to parse postBody JSON for postID {postID}"
            )
            subreddit = ""
            timestamp = ""
            score = 0
            author = ""

        internal_queue.put(
            {
                "topic": topic,  # need topic and partition in main thread to commit offsets properly
                "partition": partition,
                "offset": offset,
                "postID": postID,
                "postBody": postMsg,
                "subreddit": subreddit,
                "timestamp": timestamp,
                "score": score,
                "author": author,
            }
        )

        time.sleep(0.01)
