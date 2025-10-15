from ..configs.kafka import KAFKA_SETTINGS_CONSUMER
from ..middleware.logger import StructuredLogger
from confluent_kafka import Consumer  # type: ignore
from typing import Union, Any


# This class implements the Kafka Consumer
class KafkaConsumer:
    def __init__(self, topic: str, logger: StructuredLogger) -> None:
        self.structured_logger = logger
        try:
            self.consumer = Consumer(**KAFKA_SETTINGS_CONSUMER)
            self.consumer.subscribe([topic])

        except Exception as e:
            logger.error(event_type="Kafka", message=f"Create Consumer Error: {e}")
            raise

    # Commit Offsets after successful processing
    def commit(self, offsets: Any = None, asynchronous: bool = False) -> None:
        try:
            if offsets is not None:
                self.consumer.commit(offsets=offsets, asynchronous=asynchronous)
            else:
                self.consumer.commit(asynchronous=asynchronous)
        except Exception as e:
            self.structured_logger.error(
                event_type="Kafka",
                message=f"Offset commit failed: {e}",
            )

    # pause method: used if queue is overloaded
    def pause(self) -> None:
        self.consumer.pause(self.consumer.assignment())

    # resume method: used if queue is stabilized again
    def resume(self) -> None:
        self.consumer.resume(self.consumer.assignment())

    def poll(self, timeout_ms: int = 1000) -> Union[dict, None]:
        try:
            msg = self.consumer.poll(timeout=timeout_ms)
            if msg is None:
                return None

            return {
                "postID": msg.key().decode() if msg.key() else None,
                "postBody": msg.value().decode("utf-8"),
                "partition": msg.partition(),
                "topic": msg.topic(),
                "offset": msg.offset(),
            }

        except Exception as e:
            self.structured_logger.error(
                event_type="Kafka", message=f"Error consumer polling messages: {e}"
            )

            return None

        except Exception as e:
            print(f"error: {e}")
            return None
