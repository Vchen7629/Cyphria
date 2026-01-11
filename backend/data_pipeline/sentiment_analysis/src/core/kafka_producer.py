from src.core.kafka_config import KAFKA_SETTINGS_PRODUCER
from src.core.logger import StructuredLogger
from src.components.pub_handler import pub_handler
from confluent_kafka import Producer, KafkaError, Message  # type: ignore

# Class responsible for sending messages to a kafka topic
class KafkaProducer:
    def __init__(self, logger: StructuredLogger) -> None:
        self.structured_logger = logger

        try:
            self.producer = Producer(
                **KAFKA_SETTINGS_PRODUCER,
            )
        except Exception as e:
            self.structured_logger.error(event_type="Kafka", message=f"Create Producer error: {e}")
            exit()

    # Handler to convert kafka logs to structure handler
    def kafka_message_log_handler(self, err: KafkaError | None, msg: Message) -> None:
        if err is not None:
            self.structured_logger.error(
                event_type="Kafka",
                message=f"Failed to deliver Msg because: {msg}",
                post_id=msg.key().decode() if msg.key() else None,
            )
        else:
            self.structured_logger.info(
                event_type="Kafka",
                message="Message Delivered Successfully",
                post_id=msg.key().decode() if msg.key() else None,
                partition=msg.partition(),
                offset=msg.offset(),
                topic=msg.topic(),
            )

    # Publish the message locally
    def produce(self, topic: str, comment_id: str, processed_msg: dict[str, str | int]) -> None:
        """
        Call pub handler to publish a message to the topic with error handling

        Args:
            topic: the kafka topic to publish the msg to
            comment_id: comment id string
            processed_msg: dictionary containing the comment_id, product name, and sentiment score

        """
        pub_handler(
            producer=self.producer,
            topic=topic,
            message=processed_msg,
            postID=comment_id,
            error_topic="topic-classified-dlq",
            logger=self.structured_logger
        )

    # Call this method after produce to actually process
    def poll(self, time: str) -> None:
        self.producer.poll(time)

    # sends data to broker for ack
    def flush(self) -> None:
        self.producer.flush()
