from kafka import KafkaProducer
import os, json

class elasticsearch_producer:
    def __init__(self):
        ipaddr = os.getenv('Sentiment-Analysis-Producer-Ip','localhost:9092')
        try:
            self.producer_config = KafkaProducer(
                bootstrap_servers=[ipaddr],
                acks='all',
                key_serializer=lambda k: str(k).encode('utf-8'),
                value_serializer=lambda m: json.dumps(m).encode('utf-8')
            )
        except Exception as e:
            raise ValueError(f"error initializing the producer: {e}")