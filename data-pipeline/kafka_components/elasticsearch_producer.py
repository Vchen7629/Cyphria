import json
from kafka import KafkaProducer

#This class sends configures the producer for the elastic search topic
class ElasticSearch_Producer:
    def __init__(self):
        self.producer_config = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            acks='all',
            key_serializer=lambda k: str(k).encode('utf-8'),
            value_serializer=lambda m: json.dumps(m).encode('utf-8')
        )

    def Publish_Message(self):
        pass

ES_producer = ElasticSearch_Producer()