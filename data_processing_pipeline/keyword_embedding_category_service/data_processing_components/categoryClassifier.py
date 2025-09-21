import time
from sentence_transformers import (
    util,
)
import torch, pickle, os
import pandas as pd
import numpy as np

category_instance = None


def Get_Classifier_Instance():
    global category_instance
    if category_instance is None:
        category_instance = CategoryClassifier()
    return category_instance


class CategoryClassifier:
    def __init__(
        self,
    ):
        try:
            tensor_path = os.getenv(
                "CATEGORY_TENSOR_FILE_PATH",
                "../keyword_embedding_category_service/precomputed_category_sentences_files/category_tensor.pt",
            )
            mapping_path = os.getenv(
                "CATEGORY_MAPPING_FILE_PATH",
                "../keyword_embedding_category_service/precomputed_category_sentences_files/category_mapping.pkl",
            )

            abs_tensor_path = os.path.abspath(tensor_path)
            abs_mapping_path = os.path.abspath(mapping_path)

            if not os.path.exists(tensor_path):
                raise FileNotFoundError(f"tensor resolved path does not exist: {abs_tensor_path}.")
            print(f"Loading category tensor from: {tensor_path}")
            self.category_tensor = torch.load(tensor_path)

            if not os.path.exists(mapping_path):
                raise FileNotFoundError(
                    f"mapping resolved path does not exist: {abs_mapping_path}."
                )
            with open(
                mapping_path,
                "rb",
            ) as f:
                self.category_name = pickle.load(f)

            print(
                f"CategoryClassifier initialized with pre-computed data ({len(self.category_name)} references)."
            )
            if self.category_tensor is None or self.category_name is None:
                raise RuntimeError("Category Classifier reference embeddings failed to initialize.")
            if self.category_tensor.numel() == 0:
                print("WARN: CategoryClassifier initialized with empty reference embeddings.")
        except Exception as e:
            print(f"ERROR loading pre-computed category data: {e}")

    def Classify_Category(
        self,
        vector_embedding: pd.Series,
    ) -> pd.Series:
        try:
            t0 = time.time()
            valid_indices = vector_embedding.notna()
            valid_embeddings_list = vector_embedding[valid_indices].tolist()

            if not valid_embeddings_list:
                return pd.Series(
                    [None] * len(vector_embedding),
                    dtype=object,
                )

            numpy_array = np.array(
                valid_embeddings_list,
                dtype=np.float32,
            )
            input_tensor = torch.from_numpy(numpy_array)

            t1 = time.time()
            sim = util.semantic_search(
                input_tensor,
                self.category_tensor,
                top_k=1,
            )
            print(f"Semantic search in: {time.time() - t1:.4f} seconds")

            results = []
            for sim_list in sim:
                if sim_list:
                    best_sim_category_index = sim_list[0]["corpus_id"]
                    category_name = self.category_name[best_sim_category_index]
                    results.append(category_name)
                else:
                    results.append(None)

            print(f"Classified entirely took: {time.time() - t0:.4f} seconds")
            return pd.Series(results)

        except Exception as e:
            print(f"Error classifying category. Error: {e}")
            return pd.Series([None] * len(vector_embedding))
