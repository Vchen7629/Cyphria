# Class responsible for sending messages to a kafka topic
from ..config.kafka import KAFKA_SETTINGS
from ..middleware.logger import StructuredLogger
from confluent_kafka import Producer  # type: ignore
import json
from typing import Mapping, Any


class KafkaClient:
    def __init__(
            self, 
            logger: StructuredLogger,
            bootstrap_server: str
        ) -> None:
        self.structured_logger = logger  # logger instance
        try:
            self.producer = Producer({
                **KAFKA_SETTINGS,  # adding kafka settings
                "bootstrap.servers": bootstrap_server
                # logger=kafka_logger # logging setup messages
            })
            print("Producer connected...")

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

    # This sends a single message to kafka topic
    def send_message(
        self,
        topic: str,  # kafka topic
        message_body: Mapping[str, Any],  # reddit post body
        postID: str,  # reddit post id to be used as key
    ) -> None:
        try:
            json_str = json.dumps(message_body)
            self.producer.produce(
                topic,
                key=postID.encode("utf-8"),
                value=json_str.encode("utf-8"),
                callback=self.kafka_message_log_handler,
            )

            self.producer.flush()  # Block until all buffered messages are sent and acknowledged

        except Exception as e:
            raise RuntimeError(f"Error sending message: {e}")
