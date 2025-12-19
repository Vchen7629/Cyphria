from src.components.fetch_post import get_posts
from src.preprocessing.relevant_fields import process_post, RedditPost
from src.preprocessing.url_remover import remove_url
from src.preprocessing.demojify import demojify
from src.config.reddit_client import createRedditClient
from src.middleware.kafka_producer import KafkaClient
from src.preprocessing.check_english import detect_english
from src.middleware.logger import StructuredLogger
import praw
import json
import prawcore


class Worker:
    def __init__(
        self,
        kafka_client=None,  # Dependency Injection Kafka Client for Testing
    ):
        self.logger = StructuredLogger(pod="idk")
        self.kafka_producer = kafka_client or KafkaClient(self.logger, bootstrap_server="localhost:9092")
        self.reddit_client = createRedditClient()

    def post_message(self):
        try:
            posts: list[praw.models.Submission] = list(
                get_posts(self.reddit_client, "all", self.logger)
            )

            for post in posts:
                extracted = process_post(
                    post, self.logger
                )  # extracting only relevant parts of the api response
                url_removed = remove_url(post)
                demojified = demojify

                processed_post = RedditPost(
                    body=demojified,
                    subreddit=extracted.subreddit,
                    timestamp=extracted.timestamp,
                    post_id=extracted.post_id,
                )

                lang = detect_english(url_removed)
                if lang != "en":  # If the post is non-english skip it
                    continue

                try:
                    self.kafka_producer.send_message(
                        topic="raw-data",
                        message_body=json.loads(processed_post.model_dump_json()),
                        postID=processed_post.post_id,
                    )
                except Exception as e:
                    raise e

            print("flushing")
            self.kafka_producer.flush()
        except prawcore.exceptions.ServerError:  # Wrong Subreddit Name error handling
            self.logger.error(
                event_type="Reddit Api",
                message="Server Error",
            )
        except Exception as e:
            self.logger.error(
                event_type="Reddit Api",
                message=f"Post Fetch Error: {e}",
            )


if __name__ == "__main__":
    for i in range(1):
        Worker().post_message()
