from src.core.kafka_producer import KafkaClient


def test_consumer(
    timeout=10000000000,
):
    print("Reading message")
    try:
        consumer = KafkaClient()
        print("Waiting for messages...")
        for message in consumer:
            print(f"Received: {message.value}")
        consumer.close()
    except Exception as e:
        print(f"Error consuming messages: {e}")


if __name__ == "__main__":
    test_consumer()
