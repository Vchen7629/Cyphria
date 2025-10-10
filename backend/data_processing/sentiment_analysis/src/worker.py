from src.middleware.logger import StructuredLogger
from src.middleware.kafka_consumer import KafkaConsumer
from src.middleware.kafka_producer import KafkaProducer
from src.config.model import sentiment_analysis_model
from src.preprocessing.sentiment_analysis import Aspect_Based_Sentiment_Analysis


class StartService:
    def __init__(self) -> None:
        self.structured_logger = StructuredLogger(pod="idk2")
        self.consumer = KafkaConsumer(topic="sentiment-analysis", logger=self.structured_logger)
        self.producer = KafkaProducer(logger=self.structured_logger)
        model_data = sentiment_analysis_model("yangheng/deberta-v3-base-absa-v1.1")
        if model_data is None:
            raise RuntimeError("Failed to load sentiment analysis model")
        tokenizer, model = model_data
        self.ABSA = Aspect_Based_Sentiment_Analysis(tokenizer, model)

    def run(self) -> None:
        # data = self.consumer.poll_for_new_messages()
        data = [
            ("abc123", "The controller feels cheap but the graphics are amazing.", "controller"),
            ("abc123", "The controller feels cheap but the graphics are amazing.", "graphics"),
            ("abc124", "I poked the cat. Then i found a tasty marshmellow", "cat"),
            ("abc124", "I poked the cat. Then i found an alright marshmellow", "marshmellow"),
        ]

        sentiment_analysis = self.ABSA.SentimentAnalysis(data)

        print(sentiment_analysis)

        for item in sentiment_analysis:
            try:
                self.producer.send_message(topic="aggregator", message_body=item, postID=item[0])
            except Exception as e:
                print(f"error: {e}")
                raise e

        # After processing is done and sent to the next topic
        self.consumer.commit(asynchronous=False)
        self.structured_logger.info(
            event_type="Kafka",
            message="Offsets committed successfully after processing batch",
        )


if __name__ == "__main__":
    StartService().run()
