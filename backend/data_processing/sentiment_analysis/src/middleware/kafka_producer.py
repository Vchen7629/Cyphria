from ..config.kafka import KAFKA_SETTINGS_PRODUCER
from ..middleware.logger import StructuredLogger
from confluent_kafka import Producer, KafkaError, Message  # type: ignore
import json


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

    def send_message(self, topic: str, message_body: tuple[str, str, int], postID: str) -> None:
        try:
            json_str = json.dumps(message_body)
            self.producer.produce(
                topic,
                key=postID.encode("utf-8"),
                value=json_str.encode("utf-8"),
                callback=self.kafka_message_log_handler,
            )

            self.producer.flush()
        except Exception as e:
            raise RuntimeError(f"Error sending message: {e}")
