import pandas as pd
import time

from components import (
    sbert_model,
)

embedder_instance = None


def get_vector_embedder():
    global embedder_instance
    if embedder_instance is None:
        embedder_instance = Gen_Vector_Embeddings()
    return embedder_instance


class Gen_Vector_Embeddings:
    def __init__(
        self,
    ):
        self.model = sbert_model.get_model()

    def Generate_Vector_Embeddings(
        self,
        query: pd.Series,
    ) -> pd.Series:
        try:
            start_time = time.time()
            embeddings = self.model.encode(
                query.tolist(),
                batch_size=256,
            )
            print(f"Classified in: {time.time() - start_time:.4f}")
            return pd.Series(list(embeddings))
        except Exception as e:
            print(f"Error generating embedding batch. Error: {e}")
            return pd.Series([None] * len(query))
