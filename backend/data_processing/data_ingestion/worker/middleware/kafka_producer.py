# Class responsible for sending messages to a kafka topic
from config.kafka import KAFKA_SETTINGS
from kafka import (
    KafkaProducer,
)
import json


class KafkaClient:
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                **KAFKA_SETTINGS,
                key_serializer=lambda k: str(k).encode("utf-8"),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            print("Producer connected...")

        except Exception as e:
            print(f"Error connecting to kafka broker: {e}")
            exit()

    def Send_Message(
        self,
        topic: str,  # kafka topic
        message_body: dict,  # reddit post body
        on_success=None,
        on_error=None,
    ):
        try:
            future = self.producer.send(topic, value=message_body)

            if on_success:
                future.add_callback(on_success)
            if on_error:
                future.add_callback(on_error)
            self.producer.flush()  # Block until all buffered messages are sent and acknowledged

        except Exception as e:
            raise RuntimeError(f"Error sending message: {e}")
