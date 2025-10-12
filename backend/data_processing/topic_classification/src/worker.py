from src.middleware.kafka_consumer import KafkaConsumer
from src.middleware.kafka_producer import KafkaProducer
from src.config.sbert_model import get_model
from src.preprocessing.keywordextraction import KeywordExtraction
from src.middleware.logger import StructuredLogger
from src.components.queue import bounded_internal_queue
from queue import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from src.components.batch import batch
from src.config.types import ProcessedItem
from src.components.offsets import offset_helper
from src.components.pub_handler import pub_handler
from keybert import KeyBERT  # type: ignore

keyword_model_instance = None


def getModel():  # type: ignore
    global keyword_model_instance
    if not keyword_model_instance:
        keyword_model_instance = Start_Service()
    return keyword_model_instance


# This class defines the entry point
class Start_Service:
    def __init__(self) -> None:
        self.structured_logger = StructuredLogger(pod="idk")
        self.queue: Queue = Queue(maxsize=1000)  # processing queue
        self.consumer = KafkaConsumer(topic="raw-data", logger=self.structured_logger)
        self.producer = KafkaProducer(logger=self.structured_logger)
        self.model = get_model()
        self.kw_model = KeyBERT(model=self.model)
        self.executor = ThreadPoolExecutor(max_workers=1)

    def run(self) -> None:
        t = Thread(
            target=bounded_internal_queue,
            kwargs={
                "consumer": self.consumer,
                "high_wm": 800,
                "low_wm": 400,
                "structured_logger": self.structured_logger,
                "internal_queue": self.queue,
                "running": True,
            },
            daemon=True,  # this makes this thread stop with main thread
        )
        t.start()

        for postMsgs, postIDs, currBatch in batch(batch_size=65, queue=self.queue):
            try:
                processed_data: list[ProcessedItem] = KeywordExtraction(
                    postMsgs=postMsgs, postIDs=postIDs, executor=self.executor, model=self.kw_model
                )

                for item in processed_data:
                    pub_handler(
                        topic="test",
                        error_topic="test-dlq",
                        producer=self.producer,
                        message=item["keywords"],
                        postID=item["post_id"],
                        logger=self.structured_logger,
                    )

                self.producer.flush()

                offset_helper(
                    batch=currBatch, consumer=self.consumer, logger=self.structured_logger
                )

            except Exception as e:
                print(f"error: {e}")
                return


if __name__ == "__main__":
    Start_Service().run()
