from typing import Callable
import scipy.sparse as sp

class TestCategoryCombiner:
    def setup_method(self):
        self.mock_sentences = [
            "My new prebuilt pc has an RTX 3070 and an intel i7 12700K.",
            "I adopted a new golden retriever puppy.",
            "I'm learning how to play the piano and its awesome!"
        ]

        self.vocab = {
            'animal': ['puppy', 'dog', 'golden retriever'],
            'travel': ['airline', 'travel', 'luggage'],
            'instrument': ['instrument', 'piano', 'play'],
            'technology': ['pc', 'technology', 'intel'],
            'empty': []
        }

    def test_correct_shape(self, createNewColumns: Callable[[list[str], dict[str, list[str]]], list[sp.csr_matrix]]):
        result = createNewColumns(self.mock_sentences, self.vocab)
        animal_score = result[1]
        post1_animal_score = animal_score[0, 0]
        print("hi: ", animal_score)

        assert result == []


