from typing import TypedDict


class QueueMessage(TypedDict):
    topic: str
    partition: int
    offset: int
    postID: str
    postBody: str


class ProcessedItem(TypedDict):
    keywords: list[str]  # or Sequence[str]
    post_id: str
