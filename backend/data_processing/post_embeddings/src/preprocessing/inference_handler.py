# Handler for computing sentence embeddings using BERT
from typing import Tuple
import numpy as np
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime

def inference_handler(  # type: ignore
    post_id_list: list[str],
    post_body_list: list[str],
    subreddit_list: list[str],
    timestamp_list: list[datetime],
    model,
    timeout: int,
    executor: ThreadPoolExecutor,
) -> list[Tuple[str, np.ndarray, datetime, str]]:
    if not post_body_list:
        return []
    
    # compute the embeddings for the post in a batch
    future = executor.submit(model.encode, post_body_list, convert_to_numpy=True)

    # Error handling in case model takes too long
    try:
        post_embeddings = future.result(timeout=timeout)
    except TimeoutError:
        raise TimeoutError("Embedding Computation timed out")

    # combine all of them back into one list
    full_embedding = list(zip(post_id_list, post_embeddings, timestamp_list, subreddit_list))

    return full_embedding
