# Helper function for extracting Relevant fields for ABSA
from typing import List
import json
from confluent_kafka import Message  # type: ignore


# This extracts the reddit post text and keywords and adds the pair of sentence
# and keyword for every keyword associated with the post
def extract_pairs(msg: Message) -> List[tuple[str, str]]:
    postBody = json.loads(msg.value())

    reddit_post = postBody.get("body", "").strip()
    keywords = postBody.get("keywords", [])

    if not reddit_post or not keywords:
        return []

    batch = []

    for kw in keywords:
        batch.append((reddit_post, kw))

    return batch
