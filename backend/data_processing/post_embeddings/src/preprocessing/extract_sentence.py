# Helper function to extract only the sentence from kafka message
from confluent_kafka import Message  # type: ignore
import json
from datetime import datetime
from typing import Tuple


def extract_post_body(msg: Message) -> Tuple[str, datetime, str] | None:
    data = json.loads(msg)
    reddit_post: str = data.get("body")
    timestamp: datetime = data.get("timestamp")
    subreddit: str = data.get("subreddit")

    if not reddit_post:
        return None
    
    return reddit_post, timestamp, subreddit
