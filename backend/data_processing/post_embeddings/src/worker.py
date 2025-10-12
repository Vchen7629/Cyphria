from src.config.model import get_model
from src.middleware.kafka_consumer import KafkaConsumer
from src.middleware.kafka_producer import KafkaProducer
from src.middleware.logger import StructuredLogger
from src.components.queue import bounded_internal_queue
from src.components.batch import batch
from src.preprocessing.inference_handler import inference_handler
from src.components.offsets import offset_helper
from src.components.pub_handler import pub_handler
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from queue import Queue


class SentenceEmbeddings:
    def __init__(self) -> None:
        self.structured_logger = StructuredLogger(pod="idk")
        self.model = get_model(device="cpu", logger=self.structured_logger)
        self.consumer = KafkaConsumer(topic="raw-data", logger=self.structured_logger)
        self.producer = KafkaProducer(logger=self.structured_logger)
        self.queue: Queue = Queue(maxsize=1000)  # processing queue
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

        # Generator loop that flushes batch once iterator is done
        for post_ids, post_bodies, curr_batch in batch(self.queue, batch_size=65):
            # Feed lists to embedding model to do inference and returns a dict with id, embedding kv pair
            try:
                embeddings = inference_handler(
                    post_id_list=post_ids,
                    post_body_list=post_bodies,
                    model=self.model,
                    timeout=3,
                    executor=self.executor,
                )
            except TimeoutError:
                # Todo: Convert this logic to send it to a dlq instead of just printing
                # and continuing to reprocess later.
                print("Batch timed out — skipping this batch")
                continue

            # pushing the processed messages to kafka topic
            for pid, emb in embeddings.items():
                # convert numpy array to list for kafka, need to convert back to numpy array in other
                # services to use. if i want more compact i should use base64 but thats more complicated
                emb_list = emb.tolist()

                pub_handler(
                    producer=self.producer,
                    topic="sentence-embeddings",
                    message=emb_list,
                    postID=pid,
                    error_topic="sentence-embeddings-dlq",
                    logger=self.structured_logger,
                    max_retries=3,
                )

            # Commiting offsets to broker to confirm processing is done and sent
            offset_helper(batch=curr_batch, consumer=self.consumer, logger=self.structured_logger)


if __name__ == "__main__":
    SentenceEmbeddings().run()
