from queue import Queue
from typing import Generator, Optional
from ..configs.custom_types import QueueMessage
import time
import numpy as np
from datetime import datetime
import json


def batch(
    queue: Queue, max_batch_size: int, max_wait: float = 2.0
) -> Generator[
    tuple[list[str], list[np.ndarray], list[datetime], list[str], list[QueueMessage]], None, None
]:
    batch: list[QueueMessage] = []
    start_time: Optional[float] = time.time()

    while True:
        try:
            if not queue.empty() and len(batch) < max_batch_size:
                batch.append(queue.get())
                if start_time is None:  # Start timer on first fetch
                    start_time = time.time()

            if batch and (
                len(batch) >= max_batch_size
                or (start_time and time.time() - start_time >= max_wait)
            ):
                post_ids: list[str] = []
                embeddings: list[np.ndarray] = []
                timestamps: list[datetime] = []
                subreddits: list[str] = []

                for msg in batch:
                    post_ids.append(msg["postID"])
                    body = json.loads(msg["postBody"])

                    embeddings.append(np.array(body["embedding"]))
                    timestamps.append(body["timestamp"])
                    subreddits.append(body["subreddit"])

                yield post_ids, embeddings, timestamps, subreddits, batch

                # after main loop processes this runs and flushes batch
                batch.clear()
                start_time = None  # restart timer after everything is done

            else:
                time.sleep(0.01)
        except Exception as e:
            print(f"Error in batching: {e}")
            batch.clear()
            start_time = None
