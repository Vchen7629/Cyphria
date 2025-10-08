from ..middleware.logger import StructuredLogger
from typing import Sequence

class KeywordExtraction:
    def __init__(self, model, logging: StructuredLogger) -> None:
        self.model = model
        self.logger = logging

    # This uses Keybert with the input tuple to extract keywords per item
    def KeywordExtraction(
        self,
        postMsgs: list[str],  # posts extracted from kafka message
        postIDs: list[str],  # post ids for identifying
    ) -> list[dict[str, Sequence[str]]]:
        result = []

        for post_msg, post_id in zip(postMsgs, postIDs):
            if not post_msg.strip():  # empty or whitespace-only posts
                result.append({"keywords": [], "post_id": post_id})
                continue

            raw_keybert_output = self.model.extract_keywords(
                post_msg,
                stop_words="english",
                use_mmr=True,
                diversity=0.7,
            )

            # print(f"DEBUG: raw_keybert_output : {raw_keybert_output}")
            self.logger.debug(
                event_type="topic-classification",
                message=f"raw_keybert_output : {raw_keybert_output}",
                postID=post_id,
            )

            kw_list = []

            # extracting only keywords since raw keybert output also gives score
            for kw_item in raw_keybert_output:
                if isinstance(kw_item, tuple) and len(kw_item) == 2:
                    kw_list.append(kw_item[0])
                elif isinstance(kw_item, str):
                    kw_list.append(kw_item)

            result.append({"keywords": kw_list, "post_id": post_id})

        # combining them
        return result
