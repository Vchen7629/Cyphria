# Class responsible for sending messages to a kafka topic
from ..config.kafka import KAFKA_SETTINGS
from ..middleware.logger import logger
from ..preprocessing.relevant_fields import RedditPost
from confluent_kafka import Producer
import json
from typing import Mapping, Any


class KafkaClient:
    def __init__(self):
        try:
            self.producer = Producer(**KAFKA_SETTINGS) # adding kafka settings
            print("Producer connected...")

        except Exception as e:
            print(f"Error connecting to kafka broker: {e}")
            exit()

    # This sends a single message to kafka topic
    def Send_Message(
        self,
        topic: str,  # kafka topic
        message_body: Mapping[str, Any],  # reddit post body
        postID: str, # reddit post id to be used as key
    ):
        try:
            json_str = json.dumps(message_body)
            self.producer.produce(
                topic, 
                key=postID.encode("utf-8"),
                value=json_str.encode("utf-8"),
                callback=logger
            )

            self.producer.flush()  # Block until all buffered messages are sent and acknowledged

        except Exception as e:
            raise RuntimeError(f"Error sending message: {e}")
