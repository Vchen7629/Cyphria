# Helper function to extract only the sentence from kafka message
from confluent_kafka import Message  # type: ignore
import json


def extract_post_body(msg: Message) -> str | None:
    reddit_post: str = json.loads(msg)["body"]

    if not reddit_post:
        return None

    return reddit_post
