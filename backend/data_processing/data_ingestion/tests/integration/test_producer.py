# Todo: Use Testcontainers to test publishing messages to kafka
from kafka import KafkaConsumer
from src.middleware.kafka_producer import KafkaClient
from src.middleware.logger import StructuredLogger
import pytest

@pytest.mark.integration
def test_msg_sent_properly(kafka_service):
    logger = StructuredLogger(pod="idk")
    producer = KafkaClient(logger, kafka_service)
    
    # Set up test consumer
    consumer = KafkaConsumer(
        "test_topic",
        bootstrap_servers=kafka_service,
        auto_offset_reset="earliest",
        group_id="test-group",
        consumer_timeout_ms=3000,
    )

    # dummy msg to send
    dummy_msg = {
        "body": "this is placeholder body",
        "subreddit": "placeholder_subreddit",
        "timestamp": "2025-10-10T05:03:25.019957",
        "post_id": "post_id"
    }

    producer.send_message(
        topic="test_topic",
        message_body=dummy_msg,
        postID="post_id"
    )
    producer.flush()

    for msg in consumer:
        messages = msg.value

    print(messages)