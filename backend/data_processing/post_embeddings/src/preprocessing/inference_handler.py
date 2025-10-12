# Handler for computing sentence embeddings using BERT
from typing import Dict
import numpy as np
from concurrent.futures import ThreadPoolExecutor, TimeoutError


def inference_handler(  # type: ignore
    post_id_list: list[str],
    post_body_list: list[str],
    model,
    timeout: int,
    executor: ThreadPoolExecutor,
) -> Dict[str, np.ndarray]:
    if not post_body_list:
        return {}
    # compute the embeddings for the post in a batch
    future = executor.submit(model.encode, post_body_list, convert_to_numpy=True)

    # Error handling in case model takes too long
    try:
        post_embeddings = future.result(timeout=timeout)
    except TimeoutError:
        raise TimeoutError("Embedding Computation timed out")

    # match post id with its embedding
    match_id_embedding = {post_id: emb for post_id, emb in zip(post_id_list, post_embeddings)}

    return match_id_embedding
