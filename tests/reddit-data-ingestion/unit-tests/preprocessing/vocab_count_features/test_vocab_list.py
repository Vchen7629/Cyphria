import os, sys
from typing import Callable

project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../../")
)
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing_files.vocabCountFeature import (
    vocab_list,
)


class TestConstructor:
    def setup_method(self):
        self.mock_sentences = [
            "My new prebuilt pc has an RTX 3070 and an intel i7 12700K.",
            "I adopted a new golden retriever puppy.",
            "I'm learning how to play the piano and its awesome!",
        ]
        self.mock_vocab = {
            "animal": ["puppy", "dog", "golden retriever"],
            "travel": ["airline", "travel", "luggage"],
            "instrument": ["instrument", "piano", "play"],
            "technology": ["pc", "technology", "intel"],
            "empty": [],
        }

    def _convertIndiciesToWords(
        self, tfidf_indicies: list[tuple[str, int]], sentence_indicies: list[int]
    ) -> list[str]:
        reversed_vocab = {v: k for k, v in tfidf_indicies}
        words = [reversed_vocab[idx] for idx in sentence_indicies]

        return words

    def test_animal_vocab(self, setupTfidfVocab: Callable[[list[str]], dict[str, int]]):
        tfidf_vocab = setupTfidfVocab(self.mock_sentences)
        animal_indicies = vocab_list.constructor(tfidf_vocab, self.mock_vocab["animal"])
        words = self._convertIndiciesToWords(tfidf_vocab.items(), animal_indicies)

        assert words == ["puppy", "golden retriever"]

    def test_instrument_vocab(
        self, setupTfidfVocab: Callable[[list[str]], dict[str, int]]
    ):
        tfidf_vocab = setupTfidfVocab(self.mock_sentences)
        instrument_indicies = vocab_list.constructor(
            tfidf_vocab, self.mock_vocab["instrument"]
        )
        words = self._convertIndiciesToWords(tfidf_vocab.items(), instrument_indicies)

        assert words == ["piano", "play"]

    def test_technology_vocab(
        self, setupTfidfVocab: Callable[[list[str]], dict[str, int]]
    ):
        tfidf_vocab = setupTfidfVocab(self.mock_sentences)
        technology_indicies = vocab_list.constructor(
            tfidf_vocab, self.mock_vocab["technology"]
        )
        words = self._convertIndiciesToWords(tfidf_vocab.items(), technology_indicies)

        assert words == ["pc", "intel"]

    def test_vocab_not_appearing_in_sentence(
        self, setupTfidfVocab: Callable[[list[str]], dict[str, int]]
    ):
        tfidf_vocab = setupTfidfVocab(self.mock_sentences)
        travel_indicies = vocab_list.constructor(tfidf_vocab, self.mock_vocab["travel"])
        words = self._convertIndiciesToWords(tfidf_vocab.items(), travel_indicies)

        assert words == []

    def test_empty_vocab_category(
        self, setupTfidfVocab: Callable[[list[str]], dict[str, int]]
    ):
        tfidf_vocab = setupTfidfVocab(self.mock_sentences)
        empty_indicies = vocab_list.constructor(tfidf_vocab, self.mock_vocab["empty"])
        words = self._convertIndiciesToWords(tfidf_vocab.items(), empty_indicies)

        assert words == []
