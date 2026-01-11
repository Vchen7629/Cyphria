from src.core.logger import StructuredLogger
from src.core.kafka_consumer import KafkaConsumer
from src.core.kafka_producer import KafkaProducer
from src.core.model import sentiment_analysis_model
from src.core.types import QueueMessage
from src.preprocessing.sentiment_analysis import Aspect_Based_Sentiment_Analysis
from src.components.queue import bounded_internal_queue
from src.components.batch import batch
from src.components.offsets import offset_helper
from queue import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

class StartService:
    def __init__(self) -> None:
        self.structured_logger = StructuredLogger(pod="idk2")
        self.consumer = KafkaConsumer(topic="raw-data", logger=self.structured_logger)
        self.producer = KafkaProducer(logger=self.structured_logger)
        self.queue: Queue[QueueMessage] = Queue(maxsize=1000)
        self.executor = ThreadPoolExecutor(max_workers=1)
        model_data = sentiment_analysis_model("yangheng/deberta-v3-base-absa-v1.1")
        tokenizer, model = model_data
        self.ABSA = Aspect_Based_Sentiment_Analysis(tokenizer, model, self.executor)

    def run(self) -> None:
        t = Thread(
            target=bounded_internal_queue,
            kwargs={
                "consumer": self.consumer,
                "high_wm": 800,
                "low_wm": 400,
                "structured_logger": self.structured_logger,
                "internal_queue": self.queue,
            },
            daemon=True,  # this makes this thread stop with main thread
        )
        t.start()

        for post_id_mappings, all_product_pairs, curr_batch in batch(self.queue, batch_size=65):
            # Run sentiment analysis on all product pairs in batch
            sentiment_results = self.ABSA.SentimentAnalysis(all_product_pairs)

            print(f"Processed {len(sentiment_results)} sentiment results from {len(post_id_mappings)} posts")

            # Map sentiment results back to post_ids and publish individually
            for post_id, start_idx, end_idx, metadata in post_id_mappings:
                # Extract sentiment results for this specific post using index range
                post_sentiments = sentiment_results[start_idx:end_idx]

                # Publish each sentiment result with its correct post_id and metadata
                for product_name, sentiment_score in post_sentiments:
                    try:
                        # Create message payload with metadata
                        message = {
                            "comment_id": post_id,
                            "product": product_name,
                            "sentiment": sentiment_score,
                            "subreddit": metadata["subreddit"],
                            "timestamp": metadata["timestamp"],
                            "score": metadata["score"],
                            "author": metadata["author"]
                        }

                        self.producer.produce(
                            topic="aggregated",
                            comment_id=post_id,
                            processed_msg=message
                        )
                    except Exception as e:
                        self.structured_logger.error(
                            event_type="Kafka publish",
                            message=f"Error publishing sentiment for post {post_id}: {e}"
                        )

            # flush producer to ensure all messages are sent before committing offsets
            self.producer.flush()

            # Commit offsets to broker after processing is done and sent to next topic
            offset_helper(batch=curr_batch, consumer=self.consumer, logger=self.structured_logger)


if __name__ == "__main__":
    StartService().run()
