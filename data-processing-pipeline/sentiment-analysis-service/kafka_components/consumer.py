from kafka import KafkaConsumer
import os

class Data_Ingestion:
    def __init__(self):
        ipaddr = os.getenv('Sentiment-Analysis-Consumer-Ip','localhost:9092')

        try:
            self.consumer_config = KafkaConsumer(
                'sentiment-analysis',
                bootstrap_servers=[ipaddr],
                auto_offset_reset='latest',
                value_deserializer=lambda m: m.decode('utf-8'),
                consumer_timeout_ms=10000,
                heartbeat_interval_ms=100,
                max_poll_interval_ms=1000,
            )
        except Exception as e:
            print(f"Error setting up consumer connection to kafka topic: {e}")


