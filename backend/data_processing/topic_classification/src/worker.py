from src.middleware.kafka_consumer import KafkaConsumer
from src.middleware.kafka_producer import KafkaProducer
from src.components.sbert_model import get_model
from src.preprocessing.keywordextraction import KeywordExtraction
from src.middleware.logger import StructuredLogger

from keybert import (
    KeyBERT,
)

keyword_model_instance = None


def getModel():
    global keyword_model_instance
    if not keyword_model_instance:
        keyword_model_instance = Start_Service()
    return keyword_model_instance


# This class defines the entry point
class Start_Service:
    def __init__(self) -> None:
        self.structured_logger = StructuredLogger(pod="idk")

        self.consumer = KafkaConsumer(topic="raw-data", logger=self.structured_logger)
        self.producer = KafkaProducer(logger=self.structured_logger)
        self.model = get_model()
        kw_model = KeyBERT(model=self.model)
        self.topic_extraction = KeywordExtraction(kw_model, self.structured_logger)

    def run(self) -> None:
        while True:
            message_batch = self.consumer.poll_for_new_messages()

            if not message_batch:
                continue

            postMsgs = [msg["postBody"] for msg in message_batch]  # extract message bodies
            postIDs = [msg["postID"] for msg in message_batch]  # extract post IDs

            # This returns the processed data as a pandas dataframe
            processed_data = self.topic_extraction.KeywordExtraction(postMsgs, postIDs)

            for item in processed_data:
                try:
                    print("sending messages")
                    self.producer.send_message(
                        topic="test", message=item["keywords"], postID=item["post_id"]
                    )
                except Exception as e:
                    raise e
            
            # After processing is done and sent to the next topic
            self.consumer.commit(asynchronous=False)
            self.structured_logger.info(
                event_type="Kafka",
                message="Offsets committed successfully after processing batch",
            )

if __name__ == "__main__":
    Start_Service().run()
