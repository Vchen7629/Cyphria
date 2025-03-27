from sentence_transformers import SentenceTransformer
import time

class Gen_Vector_Embeddings:
    def __init__(self):
        start_time = time.time()

        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", backend="onnx")
        print(f"Initialized the sbert ml model in: {time.time() - start_time:.4f} seconds")

    def Generate_Vector_Embeddings(self, query):
        embeddings = self.model.encode(query)
        
        return embeddings

Embedding = Gen_Vector_Embeddings()

