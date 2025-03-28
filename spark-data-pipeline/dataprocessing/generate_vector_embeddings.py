import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components import sbert_model

class Gen_Vector_Embeddings:
    def __init__(self):
        self.model = sbert_model.get_model()
    
    def Generate_Vector_Embeddings(self, query):
        embeddings = self.model.encode(query)
        return embeddings

Embedding = Gen_Vector_Embeddings()

