from queue import Queue
from typing import Generator
from ..configs.custom_types import QueueMessage
import time
import numpy as np


def batch(
    queue: Queue, max_batch_size: int, max_wait: float = 2.0
) -> Generator[tuple[list[np.ndarray], list[str], list[QueueMessage]], None, None]:
    batch: list[QueueMessage] = []
    start_time = time.time()

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
                embeddings: list[np.ndarray] = [msg["embeddings"] for msg in batch]
                post_ids: list[str] = [msg["postID"] for msg in batch]

                yield embeddings, post_ids, batch

                # after main loop processes this runs and flushes batch
                batch.clear()
                start_time = None  # restart timer after everything is done

            else:
                time.sleep(0.01)
        except Exception as e:
            print(f"Error in batching: {e}")
            batch.clear()
            start_time = None
