from ..config.kafka import KAFKA_SETTINGS_PRODUCER
from ..middleware.logger import StructuredLogger
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
    def produce(self, topic: str, key: list[str], value: tuple[str, int]) -> None:
        self.producer.produce(
            topic=topic, key=key, value=value, callback=self.kafka_message_log_handler
        )

    # Call this method after produce to actually process
    def poll(self, time: str) -> None:
        self.producer.poll(time)

    # sends data to broker for ack
    def flush(self) -> None:
        self.producer.flush()
