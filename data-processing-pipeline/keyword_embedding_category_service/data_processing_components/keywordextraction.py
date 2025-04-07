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
        print("ok", texts_series)
        batch_start_time = time.time()
        original_index = texts_series.index
        input_batch_size = len(texts_series)

        texts_list = texts_series.astype(str).fillna("").tolist()
        raw_keybert_output = self.kw_model.extract_keywords(
            texts_list,
            stop_words="english",
            use_mmr=True,
            diversity=0.7
        )

        print(f"DEBUG: raw_keybert_output : {raw_keybert_output}")

        keywords_parsed = []
        if input_batch_size == 1:

            if len(raw_keybert_output) > 0 and isinstance(raw_keybert_output[0], (list, tuple)):
                keywords_for_doc = [
                    item[0] for item in raw_keybert_output
                    if isinstance(item, (list, tuple)) and len(item) > 0 and isinstance(item[0], str)
                ]
                keywords_parsed.append(keywords_for_doc)
            elif len(raw_keybert_output) == 1 and isinstance(raw_keybert_output[0], list):
                doc_result = raw_keybert_output[0]
                keywords_for_doc = [
                    item[0] for item in doc_result
                    if isinstance(item, (list, tuple)) and len(item) > 0 and isinstance(item[0], str)
                ]
                keywords_parsed.append(keywords_for_doc)
            elif len(raw_keybert_output) == 0:
                print("DEBUG: Handling single document empty list output.")
                keywords_parsed.append([])
            else:
                print(f"WARN: Unexpected output format for single document. Output: {raw_keybert_output}. Returning empty list for doc.")
                keywords_parsed.append([])
        elif len(raw_keybert_output) == input_batch_size:
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
                    keywords_parsed.append([])
        else:
            print(f"ERROR: KeyBERT output length ({len(raw_keybert_output)}) does not match input size ({input_batch_size}). Returning Nones.")
            return pd.Series([None] * input_batch_size, index=original_index)
        
        if len(keywords_parsed) != input_batch_size:
            print(f"CRITICAL ERROR: keywords_parsed length ({len(keywords_parsed)}) mismatch with input size ({input_batch_size}) before Series creation. Problematic raw output: {raw_keybert_output}. Returning Nones.")
            return pd.Series([None] * input_batch_size, index=original_index)

        batch_duration = time.time() - batch_start_time
        print(f"Keyword extraction batch (size {input_batch_size}) finished in: {batch_duration:.4f} seconds.")

        return pd.Series(keywords_parsed, index=original_index)
        