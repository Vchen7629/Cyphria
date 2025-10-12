from ..preprocessing.extract_sentence import extract_post_body
from ..config.my_types import QueueMessage
from queue import Queue
from typing import Generator, Tuple, List
import time


def batch(
    queue: Queue, batch_size: int, max_wait: float = 2.0
) -> Generator[Tuple[List[str], List[str], List[QueueMessage]], None, None]:
    batch: list[QueueMessage] = []
    batch_start = None  # track when the batch started

    while True:
        try:
            if not queue.empty() and len(batch) < batch_size:
                batch.append(queue.get())
                if batch_start is None:  # Start timer on first fetch
                    batch_start = time.time()

            # If batch exists and batch is at the desired size or max wait time has passed we should
            # create the lists and return them
            if batch and (
                len(batch) >= batch_size or (batch_start and time.time() - batch_start >= max_wait)
            ):
                postMsgs: list[str] = [msg["postBody"] for msg in batch]  # extract message bodies

                post_ids: list[str] = [msg["postID"] for msg in batch]  # extract post IDs
                # extract sentences only from Raw post
                post_bodies: list[str] = [
                    extract_post_body(msg_body) or "" for msg_body in postMsgs
                ]

                yield post_ids, post_bodies, batch  # Generator

                # after main loop processes this runs and flushes batch
                batch.clear()
                batch_start = None  # restart timer after everything is done

            else:
                time.sleep(0.01)
        except Exception as e:
            print(f"Error in batching: {e}")
            batch.clear()
            batch_start = None
