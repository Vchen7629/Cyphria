from typing import Callable
import scipy.sparse as sp

class TestCreator:
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

    def test_animal_score(self, calculateCategoryScore: Callable[[list[str]], list[sp.csr_matrix]]):
        scores = calculateCategoryScore(self.mock_sentences, self.vocab)

        animal_score = scores[0]
        post1_animal_score = animal_score[0, 0]
        post2_animal_score = animal_score[1, 0]
        post3_animal_score = animal_score[2, 0]

        assert post1_animal_score == 0 
        assert post2_animal_score > 0
        assert post3_animal_score == 0

    def test_travel_score(self, calculateCategoryScore: Callable[[list[str]], list[sp.csr_matrix]]):
        scores = calculateCategoryScore(self.mock_sentences, self.vocab)

        travel_score = scores[1]
        post1_travel_score = travel_score[0, 0]
        post2_travel_score = travel_score[1, 0]
        post3_travel_score = travel_score[2, 0]

        assert post1_travel_score == 0
        assert post2_travel_score == 0
        assert post3_travel_score == 0

    def test_instrument_score(self, calculateCategoryScore: Callable[[list[str]], list[sp.csr_matrix]]):
        scores = calculateCategoryScore(self.mock_sentences, self.vocab)

        instrument_score = scores[2]
        post1_instrument_score = instrument_score[0, 0]
        post2_instrument_score = instrument_score[1, 0]
        post3_instrument_score = instrument_score[2, 0]

        assert post1_instrument_score == 0
        assert post2_instrument_score == 0
        assert post3_instrument_score > 0

    def test_technology_score(self, calculateCategoryScore: Callable[[list[str]], list[sp.csr_matrix]]):
        scores = calculateCategoryScore(self.mock_sentences, self.vocab)

        technology_score = scores[3]
        post1_technology_score = technology_score[0, 0]
        post2_technology_score = technology_score[1, 0]
        post3_technology_score = technology_score[2, 0]

        assert post1_technology_score > 0
        assert post2_technology_score == 0
        assert post3_technology_score == 0
    
    def test_empty_category_score(self, calculateCategoryScore: Callable[[list[str]], list[sp.csr_matrix]]):
        scores = calculateCategoryScore(self.mock_sentences, self.vocab)

        empty_category_score = scores[4]
        post1_empty_category_score = empty_category_score[0, 0]
        post2_empty_category_score = empty_category_score[1, 0]
        post3_empty_category_score = empty_category_score[2, 0]

        assert post1_empty_category_score == 0
        assert post2_empty_category_score == 0
        assert post3_empty_category_score == 0

    def test_correct_shape(self, calculateCategoryScore: Callable[[list[str]], list[sp.csr_matrix]]):
        scores = calculateCategoryScore(self.mock_sentences, self.vocab)
        
        assert len(scores) == len(self.vocab)
        
        for i, score_matrix in enumerate(scores):
            assert score_matrix.shape == (len(self.mock_sentences), 1), f"Score at index {i} has incorrect shape: {score_matrix.shape}"