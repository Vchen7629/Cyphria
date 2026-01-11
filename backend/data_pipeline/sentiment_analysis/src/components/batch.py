from src.preprocessing.extract_pairs import extract_pairs
from src.core.types import QueueMessage
from queue import Queue
from typing import Generator, Tuple, List
import time


def batch(
    queue: Queue[QueueMessage], batch_size: int, max_wait: float = 2.0
) -> Generator[Tuple[List[Tuple[str, int, int, dict[str, str | int]]], List[tuple[str, str]], List[QueueMessage]], None, None]:
    """
    Generator that batches messages from queue and extracts product pairs while maintaining
    post id mapping and metadata

    Yields:
        Tuple containing:
        - post_id mappings: List of (post_id, start_idx, end_idx, metadata) tuples to map sentiment results back
          where metadata contains: {subreddit, timestamp, score, author}
        - all_product_pairs: flattened list of all product pairs for batch sentiment analysis
        - batch: Original batch of QueueMessages for offset commiting
    """
    batch: list[QueueMessage] = []
    batch_start: float | None = None  # track when the batch started

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
                post_id_mappings: List[Tuple[str, int, int, dict[str, str | int]]] = []
                all_product_pairs: List[Tuple[str, str]] = []
                current_idx = 0

                for msg in batch:
                    post_id = msg["postID"]
                    post_body = msg["postBody"]

                    # Extract metadata from message
                    metadata = {
                        "subreddit": msg["subreddit"],
                        "timestamp": msg["timestamp"],
                        "score": msg["score"],
                        "author": msg["author"]
                    }

                    # extract product pairs of (comment_text, product) for absa sentiment analysis to work properly
                    extracted_product_pairs: list[tuple[str, str]] = extract_pairs(post_body=post_body)

                    # Calculate the index range for this post's product pairs
                    start_idx = current_idx
                    end_idx = current_idx + len(extracted_product_pairs)

                    post_id_mappings.append((post_id, start_idx, end_idx, metadata))

                    all_product_pairs.extend(extracted_product_pairs)

                    # update current index for next post
                    current_idx = end_idx

                yield post_id_mappings, all_product_pairs, batch  # Generator

                # after main loop processes this runs and flushes batch
                batch.clear()
                batch_start = None  # restart timer after everything is done

            else:
                time.sleep(0.01)
        except Exception as e:
            print(f"Error in batching: {e}")
            batch.clear()
            batch_start = None
