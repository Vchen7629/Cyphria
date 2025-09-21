import traceback, time

from kafka_components.consumer import (
    topic_consumer,
)
from kafka_components.transform_data import (
    TransformData,
)
from kafka_components.producer import (
    Sentiment_Analysis_Producer,
)
from kafka_components.pub_message import (
    Publish_Messages,
)


# This class defines the entry point
class start_service:
    def __init__(
        self,
    ):
        transformer = None
        producer = None
        running = True
        try:
            if topic_consumer is None:
                raise ValueError("Kafka consumer instance is not initialized!")

            if Sentiment_Analysis_Producer is None:
                raise ValueError("Kafka producer instance is not initialized!")

            consumer_instance = topic_consumer()
            producer_instance = Sentiment_Analysis_Producer()
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
                        producer.publish_message(processed_df)
                    except Exception as e:
                        print(f"Error publishing message to producer: {e}")
        except Exception as e:
            print(f"Critical error during application startup or execution: {e}")
            traceback.print_exc()
        finally:
            print("INFO: Cleaning up resources...")
            if producer_instance and producer_instance.producer_config:
                try:
                    print("INFO: Closing Kafka Producer...")
                    producer_instance.producer_config.close(timeout=5)  # Add timeout
                    print("INFO: Kafka Producer closed.")
                except Exception as e_close_prod:
                    print(f"WARN: Error closing Kafka Producer: {e_close_prod}")
            else:
                print("INFO: Producer instance not available for closing.")

            if consumer_instance and consumer_instance.consumer_config:
                try:
                    print("INFO: Closing Kafka Consumer...")
                    consumer_instance.consumer_config.close()
                    print("INFO: Kafka Consumer closed.")
                except Exception as e_close_cons:
                    print(f"WARN: Error closing Kafka Consumer: {e_close_cons}")
            else:
                print("INFO: Consumer instance not available for closing.")

            print("INFO: Shutdown complete.")


if __name__ == "__main__":
    start_service()
