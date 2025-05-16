import sys, os, json, time, traceback
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_processing_components import keywordextraction, generate_vector_embeddings, categoryClassifier

class TransformData:
    def __init__(self, consumer_instance):
        self.consumer = consumer_instance 
        start_model_init = time.time()
        try:
            self.keyword_extractor = keywordextraction.KeywordExtraction()
            self.vector_embedder = generate_vector_embeddings.Gen_Vector_Embeddings()
            self.category_classifier = categoryClassifier.CategoryClassifier()
        except Exception as e:
            print(f"FATAL ERROR initializing models: {e}")
            traceback.print_exc()
            raise 

        print(f"Initialized all models in: {time.time() - start_model_init}")

    def poll_for_new_messages(self):
        extracted_data = []
        try:
            messages = self.consumer.consumer_config.poll(timeout_ms=1000) 
            if not messages:
                yield None
                return

            for tp, records in messages.items():
                for record in records:
                    if record.value:
                        try:
                            message = json.loads(record.value)
                            if isinstance(message, list):
                                 extracted_data.extend(message) 
                            elif isinstance(message, dict):
                                extracted_data.append(message)
                            else:
                                print(f"ERROR: Cannot process non-list/non-dict JSON value. Type: {type(message)}")
                        except Exception as e:
                            print(f"An unexpected error occurred for offset {record.offset}: {e}")
                    else:
                        print("records doesnt have any values")
            
            if extracted_data:
                processed_data = self.process_data(extracted_data)
                if processed_data is not None:
                    yield processed_data
                else:
                    yield None
            else:
                yield None
        except Exception as e:
            print(f"WARN: Error processing record value offset {record.offset} in {tp}: {e}. Skipping record.")
            yield None

    def process_data(self, extracted_data):
        start = time.time()
        reddit_post_dataframe = pd.DataFrame(data=extracted_data) # create initial dataframe with raw reddit post data
        try:
            keyword_series = self.keyword_extractor.Extraction(reddit_post_dataframe['body'])
            vector_embedding_series = self.vector_embedder.Generate_Vector_Embeddings(reddit_post_dataframe['body'])
            category_embeddings = self.category_classifier.Classify_Category(vector_embedding_series)
            reddit_post_dataframe['keywords'] = keyword_series
            reddit_post_dataframe['vector_embedding'] = vector_embedding_series
            reddit_post_dataframe['category'] = category_embeddings
        except Exception as e:
            raise ValueError(f"Error transforming data: {e}")
        print(f"Entire pipeline took: {time.time() - start}")
        return reddit_post_dataframe