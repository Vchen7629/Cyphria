import torch, pickle
from sbert_model import (
    get_model,
)
from category_example_sentences import (
    category_names,
)


class GenerateSentenceEmbeddingFiles:
    def __init__(
        self,
    ):
        self.model_instance = get_model()
        self.category_mapping = []
        self.embeddings_list = []

    def get_category_embeddings(
        self,
    ):
        if not category_names:
            print("Error: category_names dictionary is empty. Cannot compute embeddings.")
            return  #

        try:
            for (
                name,
                sentences,
            ) in category_names.items():
                embeddings = self.model_instance.encode(
                    sentences,
                    convert_to_tensor=True,
                )
                self.embeddings_list.append(embeddings)
                self.category_mapping.extend([name] * len(sentences))

                self.category_tensor = torch.cat(
                    self.embeddings_list,
                    dim=0,
                )
        except Exception as e:
            print(f"Error generating category embeddings. Error: {e}")

        torch.save(
            self.category_tensor,
            "../precomputed_category_sentences_files/category_tensor.pt",
        )
        pickle.dump(
            self.category_mapping,
            open(
                "../precomputed_category_sentences_files/category_mapping.pkl",
                "wb",
            ),
        )
        print("Category embeddings computed for worker.")


if __name__ == "__main__":
    print("initializing script")
    run = GenerateSentenceEmbeddingFiles()
    run.get_category_embeddings()
