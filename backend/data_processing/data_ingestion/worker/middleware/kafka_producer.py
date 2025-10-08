# Class responsible for sending messages to a kafka topic
from ..config.kafka import KAFKA_SETTINGS
from ..middleware.logger import StructuredLogger
from confluent_kafka import Producer
import json, time
from typing import Mapping, Any


class KafkaClient:
    def __init__(
        self,
        logger: StructuredLogger
    ) -> None:
        self.structured_logger = logger # logger instance
        try:
            self.producer = Producer(
                **KAFKA_SETTINGS, # adding kafka settings
                #logger=kafka_logger # logging setup messages
            )
            print("Producer connected...")

        except Exception as e:
            self.structured_logger.error(
                event_type="Error creating Kafka Producer",
                message=f"Create Producer error: {e}",
            )
            exit()
    
    # Handler to convert kafka logs to structure handler
    def Kafka_Message_Log_Handler(self, err, msg):
        if err is not None:
            self.structured_logger.error(
                event_type="Kafka Produce Error",
                message=f"Failed to deliver Msg because: {msg}",
                post_id=msg.key().decode() if msg.key() else None,
            )
        else: 
            self.structured_logger.info(
                event_type="Kafka Produce Success",
                message="Message Delivered Successfully",
                post_id=msg.key().decode() if msg.key() else None,
                partition=msg.partition(),
                offset=msg.offset(),
                topic=msg.topic(),
            )
    
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
                callback=self.Kafka_Message_Log_Handler,
            )

            self.producer.flush()  # Block until all buffered messages are sent and acknowledged

        except Exception as e:
            raise RuntimeError(f"Error sending message: {e}")
