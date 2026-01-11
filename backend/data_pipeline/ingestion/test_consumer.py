from confluent_kafka import Consumer  # type: ignore

def test_consumer() -> None:
    print("Reading message")
    consumer = None
    try:
        consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'test-group',
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe(['your-topic-name'])  # Replace with actual topic name
        print("Waiting for messages...")

        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            print(f"Received: {msg.value().decode('utf-8')}")

    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Error consuming messages: {e}")
    finally:
        if consumer is not None:
            consumer.close()

if __name__ == "__main__":
    test_consumer()
