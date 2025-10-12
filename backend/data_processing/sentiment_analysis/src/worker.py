from src.middleware.logger import StructuredLogger
from src.middleware.kafka_consumer import KafkaConsumer
from src.middleware.kafka_producer import KafkaProducer
from src.config.model import sentiment_analysis_model
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
        self.consumer = KafkaConsumer(topic="sentiment-analysis", logger=self.structured_logger)
        self.producer = KafkaProducer(logger=self.structured_logger)
        self.queue: Queue = Queue(maxsize=1000)
        model_data = sentiment_analysis_model("yangheng/deberta-v3-base-absa-v1.1")
        tokenizer, model = model_data
        self.ABSA = Aspect_Based_Sentiment_Analysis(tokenizer, model)
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

        for post_ids, keyword_pairs, curr_batch in batch(self.queue, batch_size=65):
            sentiment_analysis = self.ABSA.SentimentAnalysis(keyword_pairs)

            print(sentiment_analysis)

            for item in sentiment_analysis:
                try:
                    self.producer.produce(topic="aggregator", key=post_ids, value=item)
                except Exception as e:
                    print(f"error: {e}")
                    raise e

            # Commit offsets to broker after processing is done and sent to next topic
            offset_helper(batch=curr_batch, consumer=self.consumer, logger=self.structured_logger)


if __name__ == "__main__":
    StartService().run()
