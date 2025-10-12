from typing import TypedDict

class QueueMessage(TypedDict):
    topic: str
    partition: int
    offset: int
    postID: str
    postBody: str