import json, os
from kafka import KafkaProducer

#This class sends configures the producer for the processed data topic
class Sentiment_Analysis_Producer:
    def __init__(self):
        try:
            kafka_server = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

            self.producer_config = KafkaProducer(
                bootstrap_servers=[kafka_server],
                acks='all',
                key_serializer=lambda k: str(k).encode('utf-8'),
                value_serializer=lambda m: json.dumps(m).encode('utf-8')
            )
        except Exception as e:
            print(f"Error Initializing the producer: {e}")