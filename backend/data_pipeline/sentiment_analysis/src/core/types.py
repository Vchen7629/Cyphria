from typing import TypedDict

class QueueMessage(TypedDict):
    topic: str
    partition: int
    offset: int
    postID: str
    postBody: str
    subreddit: str
    timestamp: str  # ISO format datetime string
    score: int
    author: str
