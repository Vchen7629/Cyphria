from kafka import KafkaConsumer
import os, traceback

# This class configures and sets up a produce to consume messages from the kafka topic and apply transforms
class topic_consumer:
    def __init__(self):
        try:
            kafka_server = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
            # setting up the consume to read raw data from kafka topic
            self.consumer_config = KafkaConsumer(
                'test-topic',
                bootstrap_servers=[kafka_server],
                auto_offset_reset='latest',
                value_deserializer=lambda m: m.decode('utf-8'),
                consumer_timeout_ms=10000,
                heartbeat_interval_ms=100,
                max_poll_interval_ms=1000,
            )

        except Exception as e:
            print(f"Error setting kafka producer/consumer: {e}")
            traceback.print_exc()
            raise
    
    