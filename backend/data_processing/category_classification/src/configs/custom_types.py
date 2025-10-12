from typing import TypedDict
import numpy as np


class QueueMessage(TypedDict):
    topic: str
    partition: int
    offset: int
    postID: str
    postBody: np.ndarray
