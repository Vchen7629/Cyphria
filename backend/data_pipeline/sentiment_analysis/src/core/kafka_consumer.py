from src.core.kafka_config import KAFKA_SETTINGS_CONSUMER
from src.core.logger import StructuredLogger
from confluent_kafka import Consumer  # type: ignore
from typing import Any, Union, Tuple, Optional


# This class implements the Kafka Consumer
class KafkaConsumer:
    """Kafka consumer that consumes messages sent to the raw-data topic"""
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
        """
        Method invoked to commit the message offset after successful processing to
        prevent processed messages from being reprocessed

        Args:
            offsets: 
            asynchronous:
        """
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

    def pause(self) -> None:
        """
        Pause method invoked if queue is overloaded, there are messages 
        in the internal queue over 80% of the queue size limit
        """
        self.consumer.pause(self.consumer.assignment())

    def resume(self) -> None:
        """
        Resume method invoked if queue is stabilized again, the queue is paused
        and messages are processed until there are messages in the queue less than 
        40% of the max queue size 
        """
        self.consumer.resume(self.consumer.assignment())

    # poll method: fetch new messages from kafka topic
    def poll(self, timeout_ms: int = 1000) ->  Union[Tuple[Optional[str], str, int, str, int], None]:
        """
        method for fetching new messages from the kafka topic, polls the queue and extracts/returns
        the kafka topic message metadata. 

        Args:
            timeout_msg

        Returns:
            A tuple containing:
                - post_id: The comment ID
                - postBody: The comment json string
                - partition: Partition the msg belongs to
                - topic: The raw-data topic
                - offset: current message offset
            or None if no msg key
        """
        try:
            msg = self.consumer.poll(timeout=timeout_ms)

            postID = msg.key().decode() if msg.key() else None
            postBody = msg.value().decode("utf-8")
            partition = msg.partition()
            topic = msg.topic()
            offset = msg.offset()

            # Todo: Handle no postID, postBody, etc errors

            return postID, postBody, partition, topic, offset

        except Exception as e:
            self.structured_logger.error(
                event_type="Kafka", message=f"Error consumer polling messages: {e}"
            )

            return None
