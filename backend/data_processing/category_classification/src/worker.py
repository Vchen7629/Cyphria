from src.middleware.kafka_consumer import KafkaConsumer
from src.middleware.kafka_producer import KafkaProducer
from src.middleware.logger import StructuredLogger
from src.components.queue import bounded_internal_queue
from src.components.batch import batch
from src.components.offsets import offset_helper
from src.components.pub_handler import pub_handler
from src.configs.model import load_model
from src.preprocessing.text_classification import text_classification
from threading import Thread
from queue import Queue


class Category_Classification:
    def __init__(self) -> None:
        self.structured_logger = StructuredLogger(pod="idk3")
        self.consumer = KafkaConsumer(topic="sentence-embeddings", logger=self.structured_logger)
        self.producer = KafkaProducer(logger=self.structured_logger)
        self.model, self.label_encoder = load_model()
        self.queue: Queue = Queue(maxsize=1000)

    def run(self) -> None:
        T = Thread(
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

        T.start()

        for post_ids, embeddings, timestamps, subreddits, curr_batch in batch(
            self.queue, max_batch_size=65
        ):
            # Todo put xgboost prediction function here
            pred_labels = text_classification(self.model, self.label_encoder, embeddings)

            for post_id, category, timestamp, subreddit in zip(
                post_ids, pred_labels, timestamps, subreddits
            ):
                msg = {"category": category, "timestamp": timestamp, "subreddit": subreddit}

                pub_handler(
                    producer=self.producer,
                    topic="category-classified",
                    message=msg,
                    postID=post_id,
                    error_topic="category-classified-dlq",
                    logger=self.structured_logger,
                    max_retries=3,
                )

        offset_helper(batch=curr_batch, consumer=self.consumer, logger=self.structured_logger)


if __name__ == "__main__":
    Category_Classification().run()
