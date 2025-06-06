import pytest, sys, os
import scipy.sparse as sp
from typing import Callable
from sklearn.feature_extraction.text import TfidfVectorizer

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing.vocabCountFeature import feature_column


@pytest.fixture    
def setupTfidfVocab() -> Callable[[list[str]], dict[str, int]]:
    def _make(mock_sentences: list[str]) -> dict[str, int]:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        vectorizer.fit_transform(mock_sentences)
        return vectorizer.vocabulary_
    return _make

@pytest.fixture
def setupTfidfFeatures() -> Callable[[list[str]], list[sp.csr_matrix]]:
    def _make(mock_sentences: list[str]) -> list[sp.csr_matrix]:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        return vectorizer.fit_transform(mock_sentences)
    return _make

@pytest.fixture
def calculateCategoryScore(
    setupTfidfFeatures: Callable[[list[str]], tuple[sp.csr_matrix, dict[str, int]]],
    setupTfidfVocab: Callable[[list[str]], dict[str, int]]
) -> Callable[[list[str], dict[str, list[str]]], list[sp.csr_matrix]]:
    def _make(mock_sentences: list[str], vocab: dict[str, list[str]]) -> list[sp.csr_matrix]:
        features = setupTfidfFeatures(mock_sentences)
        tfidf_vocab = setupTfidfVocab(mock_sentences)
        return feature_column.categoryScores(features, tfidf_vocab, vocab)
    return _make

@pytest.fixture
def createNewColumns(
    setupTfidfFeatures: Callable[[list[str]], tuple[sp.csr_matrix, dict[str, int]]],
    calculateCategoryScore: Callable[[list[str], dict[str, list[str]]], list[sp.csr_matrix]]
) -> Callable[[list[str], dict[str, list[str]]], list[sp.csr_matrix]]:
    def _make(mock_sentences: list[str], vocab: dict[str, list[str]]) -> list[sp.csr_matrix]:
        features = setupTfidfFeatures(mock_sentences)
        categoryScores = calculateCategoryScore(mock_sentences, vocab)

        return feature_column.combine(categoryScores, features)
    return _make