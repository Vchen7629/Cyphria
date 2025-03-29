import time
from sentence_transformers import util
import torch
import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType, ArrayType, FloatType

from components import sbert_model, category_example_sentences
from components.category_example_sentences import category_names

category_instance = None

def Get_Classifier_Instance():
    global category_instance
    if category_instance is None:
        category_instance = CategoryClassifier()
    return category_instance

class CategoryClassifier:
    model_instance = sbert_model.get_model()
    category_embeddings_computed = False
    
        
    @classmethod
    def get_category_embeddings(cls):
        if not cls.category_embeddings_computed:
            cls.category_mapping = []
            embeddings_list = []
            for name, sentences in category_names.items():
                embeddings = cls.model_instance.encode(sentences, convert_to_tensor=True)
                embeddings_list.append(embeddings)
                cls.category_mapping.extend([name] * len(sentences))

            cls.category_tensor = torch.cat(embeddings_list, dim=0)
            cls.category_embeddings_computed = True
            print("Category embeddings computed for worker.")
        return cls.category_tensor, cls.category_mapping
    
    def __init__(self):
        self.model = self.model_instance
        self.category_tensor, self.category_name = self.get_category_embeddings()
        if self.category_tensor is None or self.category_name is None:
            raise RuntimeError("Category Classifier embeddings failed to initialize.")
        
    def Classify_Category(self, query: pd.Series) -> pd.Series:     
        try:
            input_embeddings = self.model.encode(query.tolist(), convert_to_tensor=True, batch_size=64)
            
            sim = util.semantic_search(
                input_embeddings,
                self.category_tensor,
                top_k=1
            )
            
            results = []
            for sim_list in sim:
                if sim_list:
                    best_sim_category_index = sim_list[0]['corpus_id']
                    category_name = self.category_name[best_sim_category_index]
                    results.append(category_name)
                else:
                    results.append(None)
                    
            return pd.Series(results)

        except Exception as e:
            print(f"Error generating embedding batch. Error: {e}")
            return pd.Series([None] * len(query))
            
@pandas_udf(StringType())
def Category_Classifier_Pandas_Udf(text: pd.Series) -> pd.Series:
    start_time = time.time()
    category = Get_Classifier_Instance()
    print(f"Classified Category in: {time.time() - start_time:.4f} seconds")
    return category.Classify_Category(text)
    

