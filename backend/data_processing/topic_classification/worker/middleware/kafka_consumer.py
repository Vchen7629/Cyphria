from ..config.kafka import KAFKA_SETTINGS_CONSUMER
from ..middleware.logger import StructuredLogger
from confluent_kafka import Consumer # type: ignore
import time
from typing import Optional


# This class implements the Kafka Consumer
class KafkaConsumer:
    def __init__(self, topic: str, logger: StructuredLogger):
        self.structured_logger = logger
        try:
            self.consumer = Consumer(**KAFKA_SETTINGS_CONSUMER)
            self.consumer.subscribe([topic])

        except Exception as e:
            logger.error(event_type="Kafka", message=f"Create Consumer Error: {e}")
            raise

    def poll_for_new_messages(self, timeout_ms: int = 1000) -> list[dict[str, Optional[str]]]:
        batch: list[dict[str, Optional[str]]] = []  # batch of msgs to be processed
        start = time.time()  # timer for the duration to wait before batch processing

        while len(batch) < 10 and time.time() - start < 1.0:
            try:
                msg = self.consumer.poll(timeout=timeout_ms)

                if msg is None:
                    continue
                if msg.error():
                    self.structured_logger.error(
                        event_type="Kafka", message=f"Kafka error: {msg.error()}"
                    )
                    continue

                batch.append(
                    {
                        "postID": msg.key().decode() if msg.key() else None,
                        "postBody": msg.value().decode("utf-8"),
                    }
                )

                self.structured_logger.info(
                    event_type="Kafka",
                    message="Message recieved from kafka",
                    key=msg.key().decode() if msg.key() else None,
                    topic=msg.topic(),
                    partition=msg.partition(),
                    offset=msg.offset(),
                )
            except Exception as e:
                self.structured_logger.error(
                    event_type="Kafka", message=f"Error consumer polling messages: {e}"
                )
                return []

        return batch
