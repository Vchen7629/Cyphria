from typing import Generator, Tuple, Any
from ..config.types import QueueMessage
import time
from queue import Queue


def batch(
    batch_size: int, queue: Queue, max_wait: float = 2.0
) -> Generator[Tuple[list[str], list[str], list[QueueMessage]], None, None]:
    batch: list[QueueMessage] = []  # list to store all the values pulled from queue
    batch_start: Any = None

    while True:
        try:
            if not queue.empty() and len(batch) < batch_size:
                batch.append(queue.get())
                if batch_start is None:  # Start timer on first fetch
                    batch_start = time.time()

            if batch and (
                len(batch) >= batch_size or (batch_start and time.time() - batch_start >= max_wait)
            ):
                postMsgs: list[str] = [msg["postBody"] for msg in batch]  # extract message bodies
                postIDs: list[str] = [msg["postID"] for msg in batch]  # extract post IDs

                yield postMsgs, postIDs, batch

                batch.clear()  # clear batch after processing
                batch_start = None  # restart timer after everything is done
            else:
                time.sleep(0.01)

        except Exception as e:
            print(f"Error in batching: {e}")
            batch.clear()
            batch_start = None
