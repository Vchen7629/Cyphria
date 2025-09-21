import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing_files import (
    remove_noise,
)


class TestStopwordRemover:
    def setup_method(self):
        self.stopword_instance = remove_noise.removeNoise()

    def test_stopwords_removed(self):
        test_text = "The quick brown fox jumps over the lazy dog."
        stopword_func = self.stopword_instance.stopWords(test_text)

        assert stopword_func == "quick brown fox jumps lazy dog."

    def test_works_if_emoji_present(self):
        test_text = "Which one is your favorite?😈"
        stopword_func = self.stopword_instance.stopWords(test_text)

        assert stopword_func == "one favorite?😈"
