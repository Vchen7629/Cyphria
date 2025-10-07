from worker.components.fetch_post import get_posts
from worker.preprocessing.relevant_fields import process_post, RedditPost
from worker.preprocessing.stop_words import stop_words
from worker.preprocessing.url_remover import remove_url
from worker.config.reddit_client import createRedditClient
from worker.middleware.kafka_producer import KafkaClient
from langdetect import (
    detect,
)
import praw, json


class Worker:
    def __init__(
        self,
        kafka_client=None,  # Dependency Injection Kafka Client for Testing
    ):
        self.kafka_producer = kafka_client or KafkaClient()
        self.reddit_client = createRedditClient()

    def post_message(self):
        posts: list[praw.models.Submission] = get_posts(self.reddit_client, "gaming")

        for post in posts:
            extracted = process_post(post)  # extracting only relevant parts of the api response
            no_stop_words = stop_words(extracted.body)  # removing stop words from the body
            url_removed = remove_url(no_stop_words)

            processed_post = RedditPost(
                body=url_removed,
                subreddit=extracted.subreddit,
                timestamp=extracted.timestamp,
                id=extracted.id,
            )

            if detect(no_stop_words) != "en":  # If the post is non-english skip it
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
    for i in range(1, 100):
        Worker().post_message()