from ..config.kafka import KAFKA_SETTINGS_CONSUMER
from ..middleware.logger import StructuredLogger
from ..preprocessing.extract_pairs import extract_pairs
from confluent_kafka import Consumer  # type: ignore
import time
from typing import List


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
    def commit(self, asynchronous: bool = False) -> None:
        try:
            self.consumer.commit(asynchronous=asynchronous)
        except Exception as e:
            self.structured_logger.error(
                event_type="Kafka",
                message=f"Offset commit failed: {e}",
            )

    def poll_for_new_messages(self, timeout_ms: int = 1000) -> List[tuple[str, str, str]]:
        batch: list[tuple[str, str, str]] = []  # batch of msgs to be processed
        start = time.time()  # timer for the duration to wait before batch processing

        while len(batch) < 65 and time.time() - start < 1.0:
            try:
                print("polling")
                msg = self.consumer.poll(timeout=timeout_ms)

                if msg is None:
                    continue
                if msg.error():
                    self.structured_logger.error(
                        event_type="Kafka", message=f"Kafka error: {msg.error()}"
                    )
                    continue

                if msg.key():
                    batch = extract_pairs(msg)
                else:
                    continue

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
