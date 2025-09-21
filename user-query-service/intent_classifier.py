from sentence_transformers import SentenceTransformer, util
import time


class IntentClassifier:
    def __init__(self):
        start_time = time.time()
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2", backend="onnx"
        )
        FACTUAL = (
            [
                "What is X?",
                "How does X work?",
                "Explain the concept of X",
                "What are the components of X?",
                "When was X created?",
                "What are the benefits of X?",
                "How many X are in Y?",
                "What is the purpose of X?",
            ],
        )
        OPINION = (
            [
                "Is X worth doing?",
                "Should I learn X?",
                "Do people recommend X?",
                "Would X be valuable for me?",
                "Is X better than Y for Z purpose?",
                "Would you recommend X?",
                "Is it worth investing in X?",
            ],
        )
        COMPARISON = [
            "X vs Y",
            "X or Y which is better",
            "Compare X and Y",
            "Differences between X and Y",
            "X versus Y for Z",
            "Advantages of X over Y",
            "X compared to Y",
        ]

        self.embeddings_factual = self.model.encode(FACTUAL, convert_to_tensor=True)
        self.embeddings_comparison = self.model.encode(
            COMPARISON, convert_to_tensor=True
        )
        self.embeddings_opinion = self.model.encode(OPINION, convert_to_tensor=True)
        print(f"Initialization loaded in {time.time() - start_time:.4f} seconds")

    def classify(self, query):
        start_time = time.time()
        query_embeddings = self.model.encode(query, convert_to_tensor=True)

        sim_factual = (
            util.cos_sim(query_embeddings, self.embeddings_factual).mean().item()
        )
        sim_comparison = (
            util.cos_sim(query_embeddings, self.embeddings_comparison).mean().item()
        )
        sim_opinion = (
            util.cos_sim(query_embeddings, self.embeddings_opinion).mean().item()
        )

        scores = {
            "FACTUAL": sim_factual,
            "COMPARISON": sim_comparison,
            "OPINION": sim_opinion,
        }

        print(f"Word vectors loaded in {time.time() - start_time:.4f} seconds")
        return max(scores, key=scores.get), scores


classifier = IntentClassifier()


# [4, 4]
