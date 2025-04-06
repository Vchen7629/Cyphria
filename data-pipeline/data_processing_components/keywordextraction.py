from keybert import KeyBERT
import pandas as pd
import sys, os, time, traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components import sbert_model

keyword_model_instance = None
def getModel():
    global keyword_model_instance
    if not keyword_model_instance:
        keyword_model_instance = KeywordExtraction()
    return keyword_model_instance

class KeywordExtraction:
    def __init__(self):
        self.model = sbert_model.get_model()
        self.kw_model = KeyBERT(model=self.model)

    def Extraction(self, texts_series: pd.Series) -> pd.Series:
        batch_start_time = time.time()
        original_index = texts_series.index

        try:
            texts_list = texts_series.astype(str).fillna("").tolist()
            input_batch_size = len(texts_list)

            if input_batch_size == 0:
                print("Input Series is empty. Returning empty Series.")
                return pd.Series([], dtype=object, index=original_index)

            print(f"Extracting keywords for {input_batch_size} documents...")
            keybert_start_time = time.time()

            raw_keybert_output = self.kw_model.extract_keywords(
                texts_list,
                stop_words="english",
                use_mmr=True,
                diversity=0.7
            )

            keybert_duration = time.time() - keybert_start_time
            print(f"KeyBERT call took {keybert_duration:.4f}s")

            # Validate the primary output structure and length
            if not isinstance(raw_keybert_output, list) or len(raw_keybert_output) != input_batch_size:
                print(f"ERROR: KeyBERT output type ({type(raw_keybert_output)}) or length "
                      f"({len(raw_keybert_output) if isinstance(raw_keybert_output, list) else 'N/A'}) "
                      f"does not match input size ({input_batch_size}). Returning Nones.")
                return pd.Series([None] * input_batch_size, index=original_index)
            
            keywords_parsed = []
            for doc_result in raw_keybert_output:
                if isinstance(doc_result, list):
                    # Extract keyword if item is a tuple/list with at least one string element
                    keywords_for_doc = [
                        item[0] for item in doc_result
                        if isinstance(item, (list, tuple)) and len(item) > 0 and isinstance(item[0], str)
                    ]
                    keywords_parsed.append(keywords_for_doc)
                else:
                    # Handle case where an element for a doc isn't a list (unexpected)
                    print(f"WARN: Expected list for doc results, got {type(doc_result)}. Appending empty list.")
                    keywords_parsed.append([]) # Append an empty list as a fallback

            batch_duration = time.time() - batch_start_time
            print(f"Keyword extraction batch (size {input_batch_size}) finished in: {batch_duration:.4f} seconds.")

            return pd.Series(keywords_parsed, index=original_index)

        except Exception as e:
            print(f"ERROR during keyword extraction batch: {e}")
            traceback.print_exc()
            return pd.Series([None] * len(texts_series), index=original_index)
        