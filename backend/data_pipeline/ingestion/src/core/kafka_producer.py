# Class responsible for sending messages to a kafka topic
from .kafka_config import KAFKA_SETTINGS
from .logger import StructuredLogger
from confluent_kafka import Producer, KafkaError, Message  # type: ignore
import json
from typing import Mapping, Any


class KafkaClient:
    def __init__(
            self, 
            logger: StructuredLogger,
            bootstrap_server: str
        ) -> None:
        self.structured_logger = logger  # logger instance
        self.bootstrap_server = bootstrap_server

        self._initialize_producer()

    def _initialize_producer(self) -> None:
        """Initialize and create the kafka producer instance"""
        try:
            self.producer = Producer({
                **KAFKA_SETTINGS,  # adding kafka settings
                "bootstrap.servers": self.bootstrap_server
                # logger=kafka_logger # logging setup messages
            })
            print("Producer connected...")

        except Exception as e:
            self.structured_logger.error(
                event_type="Kafka",
                message=f"Create Producer error: {e}",
            )
            exit()

    def kafka_message_log_handler(self, err: KafkaError | None, msg: Message) -> None:
        """
        Handler to convert kafka logs to structured logs format

        Args:
            err: Kafka error object, None if no error
            msg: the message object containing the produced message
        """
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
            )

    def send_message(self, topic: str, message_body: Mapping[str, Any], postID: str) -> None:
        """
        Send a single message to the designated kafka topic

        Args:
            topic: kafka topic name
            message_body: message body containing fields such as comment text, timestamp, etc
            postID: the unique id for each comment
        """

        try:
            json_str = json.dumps(message_body)
            self.producer.produce(
                topic,
                key=postID.encode("utf-8"),
                value=json_str.encode("utf-8"),
                #callback=self.kafka_message_log_handler,
            )
        except Exception as e:
            raise RuntimeError(f"Error sending message: {e}")
    
    def flush(self, timeout: float = 30.0) -> None:
        """
        Send all query messages to the broker

        Args: 
            timeout: idk
        """
        self.producer.flush(timeout)
