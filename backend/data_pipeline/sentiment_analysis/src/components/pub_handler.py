from typing import Any
from src.core.logger import StructuredLogger
import json
from time import sleep
from confluent_kafka import Producer


# Error handling for bad requests for publishing to kafka topic
def pub_handler(  # type: ignore[no-untyped-def]
    producer: Producer,
    topic: str,
    message: Any,
    postID: str,
    error_topic: str,
    logger: StructuredLogger,
    max_retries: int = 3,
) -> None:
    """
    Handler function for publishing the message to regular kafka topic
    built in error handling with retries before sending to the dlq on errors

    Args:
        producer: 
        topic: kafka topic to publish the processed messages to
        message: 
    """
    retries = 0
    json_str = json.dumps(message)
    while retries <= max_retries:
        try:
            producer.produce(
                topic=topic,
                key=postID.encode("utf-8"),
                value=json_str.encode("utf-8"),
            )

            producer.poll(0)  # poll to actually process the produce message and free the internal queue

            break
        except BufferError:
            print("Local producer queue is full, waiting...", flush=True)
            producer.poll(1)  # wait a bit, let delivery callbacks free space
            retries += 1
        except Exception as e:
            # Retry logic 3x then send to dlq
            retries += 1
            if retries > max_retries:  # Send to dlq when retried 3 times
                producer.produce(
                    topic=error_topic,
                    key=postID.encode("utf-8"),
                    value=json_str.encode("utf-8"),
                )
                logger.error(event_type="dlq", message=f"Errored out with: {e}")
                producer.poll(0)
                break  # break out
            else:  # Exponential Backoff: keep retrying until hit retry limit
                print(f"retrying: {retries}")
                sleep(2**retries)
