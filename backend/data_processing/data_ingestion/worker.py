from worker.components.fetch_post import get_posts
from worker.preprocessing.relevant_fields import process_post, RedditPost
from worker.preprocessing.stop_words import stop_words
from worker.preprocessing.url_remover import remove_url
from worker.config.reddit_client import createRedditClient
from worker.middleware.kafka_producer import KafkaClient
from worker.preprocessing.check_english import detect_english
from worker.middleware.logger import StructuredLogger
import praw
import json
import prawcore


class Worker:
    def __init__(
        self,
        kafka_client=None,  # Dependency Injection Kafka Client for Testing
    ):
        self.logger = StructuredLogger(pod="idk")
        self.kafka_producer = kafka_client or KafkaClient(self.logger)
        self.reddit_client = createRedditClient()

    def post_message(self):
        try:
            posts: list[praw.models.Submission] = list(get_posts(self.reddit_client, "gamin"))
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

        for post in posts:
            extracted = process_post(
                post, self.logger
            )  # extracting only relevant parts of the api response
            no_stop_words = stop_words(extracted.body)  # removing stop words from the body
            url_removed = remove_url(no_stop_words)

            processed_post = RedditPost(
                body=url_removed,
                subreddit=extracted.subreddit,
                timestamp=extracted.timestamp,
                id=extracted.id,
            )

            lang = detect_english(url_removed)
            if lang != "en":  # If the post is non-english skip it
                continue

            try:
                self.kafka_producer.Send_Message(
                    topic="test",
                    message_body=json.loads(processed_post.model_dump_json()),
                    postID=processed_post.id,
                )
            except Exception as e:
                raise e


if __name__ == "__main__":
    Worker().post_message()
