from kafka import KafkaConsumer

def test_consumer(timeout=100):
    print("Reading message")
    try:
        consumer = KafkaConsumer(
            'processed_data',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='latest',
            value_deserializer=lambda m: m.decode('utf-8'),
            consumer_timeout_ms=timeout * 1000
        )

        print("Waiting for messages...")
        for message in consumer:
            print(f"Received: {message.value}")
        consumer.close()
    except Exception as e:
        print(f"Error consuming messages: {e}")

if __name__ == "__main__":
    test_consumer()