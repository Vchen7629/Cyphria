from typing import TypedDict


class QueueMessage(TypedDict):
    postID: str
    postBody: str
    partition: int
    topic: str
    offset: int
