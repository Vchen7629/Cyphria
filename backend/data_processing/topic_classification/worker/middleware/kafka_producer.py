from confluent_kafka import Producer # type: ignore
from ..config.kafka import KAFKA_SETTINGS_PRODUCER
from ..middleware.logger import StructuredLogger
import json


# This class sends configures the producer for the processed data topic
class KafkaProducer:
    def __init__(self, logger: StructuredLogger) -> None:
        self.structured_logger = logger
        try:
            self.producer = Producer(**KAFKA_SETTINGS_PRODUCER)
        except Exception as e:
            self.structured_logger.error(
                event_type="Kafka",
                message=f"Create Producer error: {e}",
            )
            exit()

    # Handler to convert kafka logs to structure handler
    def kafka_message_log_handler(self, err, msg):
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

    def send_message(
        self,
        topic: str,
        message: dict[str, str],
        postID: str,
    ):
        try:
            json_str = json.dumps(message)
            self.producer.produce(
                topic,
                key=postID.encode("utf-8"),
                value=json_str.encode("utf-8"),
                callback=self.kafka_message_log_handler,
            )

            self.producer.flush()

        except Exception as e:
            print(f"Error publishing message to topic {topic}: {e}")
