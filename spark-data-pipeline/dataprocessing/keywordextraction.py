from keybert import KeyBERT
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType, ArrayType, StructType, StructField, FloatType
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
        try:
            texts_list = texts_series.fillna("").tolist()
            input_batch_size = len(texts_list)
            if input_batch_size == 0:
                return pd.Series([], dtype=object)

            print(f"DEBUG: Input to KeyBERT: {input_batch_size} documents.")
            keybert_start_time = time.time()

            raw_keybert_output = self.kw_model.extract_keywords(
                texts_list,
                stop_words="english",
            )
            keybert_duration = time.time() - keybert_start_time
            print(f"DEBUG: Raw KeyBERT output type: {type(raw_keybert_output)}, Length: {len(raw_keybert_output) if isinstance(raw_keybert_output, list) else 'N/A'}")


            keywords_parsed = []

            # CASE 1: Input was size 1, KeyBERT returned flat list of tuples
            if input_batch_size == 1 and isinstance(raw_keybert_output, list) and all(isinstance(item, tuple) for item in raw_keybert_output):
                print("DEBUG: Handling KeyBERT flat list output for single input doc.")
                single_doc_keyword_list = []
                for item in raw_keybert_output:
                     if isinstance(item, (list, tuple)) and len(item) > 0 and isinstance(item[0], str):
                         single_doc_keyword_list.append(item[0])
                     else:
                         print(f"WARN: Unexpected item format in flat list: {item}")
                keywords_parsed.append(single_doc_keyword_list)

            # CASE 2: Input size > 1, ASSUME KeyBERT returns list of lists of tuples (standard behavior)
            elif isinstance(raw_keybert_output, list) and len(raw_keybert_output) == input_batch_size:
                print("DEBUG: Handling KeyBERT list-of-lists output.")
                for i, keywords_doc in enumerate(raw_keybert_output):
                    single_doc_keyword_list = []
                    if isinstance(keywords_doc, (list, tuple)):
                        for item in keywords_doc:
                            if isinstance(item, (list, tuple)) and len(item) > 0 and isinstance(item[0], str):
                                single_doc_keyword_list.append(item[0])
                            else:
                                print(f"WARN: Unexpected item format for doc {i}: {item}")
                    else:
                        print(f"WARN: Unexpected result type for doc {i}: {type(keywords_doc)}")
                    keywords_parsed.append(single_doc_keyword_list)

            else:
                return pd.Series([None] * input_batch_size)

            batch_duration = time.time() - batch_start_time
            print(f"Keyword extraction batch (size {input_batch_size}) finished in: {batch_duration:.4f} seconds. (KeyBERT took {keybert_duration:.4f}s)")
            return pd.Series(keywords_parsed)

        except Exception as e:
            print(f"Error extracting keywords batch: {e}")
            traceback.print_exc()
            return pd.Series([None] * len(texts_series))

@pandas_udf(ArrayType(StringType()))
def Keyword_Extraction_Pandas_UDF(text: pd.Series) -> pd.Series:
    extract = getModel()
    return extract.Extraction(text)