from kafka_components.consumer import (
    Data_Ingestion,
)
from kafka_components.producer import (
    elasticsearch_producer,
)
from kafka_components.transformdata import (
    TransformData,
)
from kafka_components.publish_message import (
    PublishMessage,
)
from model.deberta import (
    deberta,
)
import traceback


class Sentiment_Analysis:
    def __init__(
        self,
    ):
        consumer_instance = None
        producer_instance = None
        running = True
        try:
            if Data_Ingestion == None:
                raise ValueError("Kafka consumer instance is not initialized!")

            if elasticsearch_producer == None:
                raise ValueError("Kafka producer instance is not initialized!")

            consumer_instance = Data_Ingestion()
            producer_instance = elasticsearch_producer()
            token = deberta.tokenizer
            model = deberta.model
            transformer = TransformData(
                consumer_instance=consumer_instance,
                tokenizer=token,
                model=model,
            )
            publisher = PublishMessage(producer_instance=producer_instance)
            while running:
                try:
                    generator_object = transformer.poll_for_new_messages()
                    processed_df = next(generator_object)
                except StopIteration:
                    print("WARN: Transformer generator stopped unexpectedly. Ending loop.")
                    running = False
                    continue
                except Exception as e:
                    traceback.print_exc()
                    processed_df = None
                    raise ValueError(f"ERROR getting data from transformer generator: {e}")

                if processed_df is not None and not processed_df.empty:
                    try:
                        publisher.Pub_Message(processed_df)
                    except Exception as e:
                        raise ValueError(f"Error sending message: {e}")

        except Exception as e:
            raise ValueError(f"Error in main.py: {e}")
        finally:
            print("INFO: Cleaning up resources...")
            if producer_instance and producer_instance.producer_config:
                try:
                    producer_instance.producer_config.close(timeout=5)  # Add timeout
                except Exception as e_close_prod:
                    raise ValueError(f"WARN: Error closing Kafka Producer: {e_close_prod}")
            else:
                print("INFO: Producer instance not available for closing.")

            if consumer_instance and consumer_instance.consumer_config:
                try:
                    print("INFO: Closing Kafka Consumer...")
                    consumer_instance.consumer_config.close()
                    print("INFO: Kafka Consumer closed.")
                except Exception as e_close_cons:
                    raise ValueError(f"WARN: Error closing Kafka Consumer: {e_close_cons}")
            else:
                print("INFO: Consumer instance not available for closing.")

            print("INFO: Shutdown complete.")


if __name__ == "__main__":
    Sentiment_Analysis()
