from sentence_transformers import SentenceTransformer
import time 

class SbertModelSingleton:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            start_time = time.time()
            cls._instance = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", backend="onnx")
            print(f"Initialized the sbert ml model in: {time.time() - start_time:.4f} seconds")
        return cls._instance

def get_model():
    return SbertModelSingleton.get_instance()