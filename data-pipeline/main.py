import traceback, time

from kafka_components.consumer import topic_consumer
from kafka_components.transform_data import TransformData
from kafka_components.elasticsearch_producer import ElasticSearch_Producer
from kafka_components.pub_message import Publish_Messages

# This class defines the entry point
class run_pipeline:
    def __init__(self):
        transformer = None
        producer = None
        running = True
        try:
            if topic_consumer is None:
                raise ValueError("Kafka consumer instance is not initialized!")
            
            consumer_instance = topic_consumer() 
            producer_instance = ElasticSearch_Producer()
            transformer = TransformData(consumer_instance=consumer_instance)
            producer = Publish_Messages(publisher_instance=producer_instance)
            while running:
                try:
                    generator_object = transformer.poll_for_new_messages()
                    processed_df = next(generator_object) 
                except StopIteration:
                    print("WARN: Transformer generator stopped unexpectedly. Ending loop.")
                    running = False
                    continue
                except Exception as e_yield:
                    print(f"ERROR getting data from transformer generator: {e_yield}")
                    traceback.print_exc()
                    processed_df = None
                    time.sleep(0.1)

                if processed_df is not None and not processed_df.empty:
                    try:
                        print(processed_df)
                        producer.publish_message(processed_df)
                        producer_instance.producer_config.close()
                    except Exception as e:
                        print(f"Error publishing message to producer: {e}")
        except Exception as e:
            print(f"Critical error during application startup or execution: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    run_pipeline()
    