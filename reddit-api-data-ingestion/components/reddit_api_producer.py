from kafka import KafkaProducer
import logging, time
import json

#logging.basicConfig(level=logging.DEBUG)


class Reddit_Api_Producer:
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                acks='all',
                retries=3,
                request_timeout_ms=15000, 
                max_block_ms=30000,
                key_serializer=lambda k: str(k).encode('utf-8'),
                value_serializer=lambda m: json.dumps(m).encode('utf-8')
            )
            print("Producer connected...")

        except Exception as e:
            print(f"Error connecting to kafka broker: {e}")
            exit()

    def on_send_success(self, record_metadata):
        print(f"Success! Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
    
    def on_send_error(self, excp):
        print(f"Error sending message: {excp}")

    def Send_Message(self, message_body):
        print("sending message")
        try:
            test_message = self.producer.send('test-topic', value=message_body)
            test_message.add_callback(r_producer.on_send_success)
            test_message.add_errback(r_producer.on_send_error)

            print("Flushing producer...")
            self.producer.flush() # Block until all buffered messages are sent and acknowledged
            print("Flush complete.")
                
        except Exception as e:
            print(f"An error occurred during send/flush: {e}")

r_producer = Reddit_Api_Producer()
