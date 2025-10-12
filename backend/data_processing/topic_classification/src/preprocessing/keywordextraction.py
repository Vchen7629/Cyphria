from ..config.types import ProcessedItem
from concurrent.futures import ThreadPoolExecutor, TimeoutError


# This uses Keybert with the input msg to extract keywords per item
def KeywordExtraction(  # type: ignore
    postMsgs: list[str],  # posts extracted from kafka message
    postIDs: list[str],  # post ids for identifying
    executor: ThreadPoolExecutor,
    model,
) -> list[ProcessedItem]:
    result: list[ProcessedItem] = []

    for post_msg, post_id in zip(postMsgs, postIDs):
        if not post_msg:  # empty or whitespace-only posts
            continue

        # using thread to run inference
        future = executor.submit(
            model.extract_keywords,
            post_msg,
            stop_words="english",
            use_mmr=True,
            diversity=0.7,
        )

        kw_list = []

        try:
            raw_output = future.result(timeout=1)  # timeout of 1 second

            for kw_item in raw_output:
                if isinstance(kw_item, tuple) and len(kw_item) == 2:
                    kw_list.append(kw_item[0])
                elif isinstance(kw_item, str):
                    kw_list.append(kw_item)

            result.append({"keywords": kw_list, "post_id": post_id})
        except TimeoutError:
            print(f"[Timeout] Keyword extraction took too long for post_id {post_id}")

            continue
        except Exception as e:
            raise e

            raw_output = []

            continue

    # combining them
    return result
