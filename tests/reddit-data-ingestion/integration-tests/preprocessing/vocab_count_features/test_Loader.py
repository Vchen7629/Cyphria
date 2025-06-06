import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing.vocabCountFeature import loader

class TestFunction:
    def setup_method(self):
        self.instance = loader.Coordinator("lexicon_datasets")

    def test_has_all_keys(self):
        key_arr = []
        expected_key_arr = [
            'jobs', 'law', 'food', 'health', 'gaming', 'history', 'animals', 'housing', 'business', 'gardening',
            'literature', 'investments', 'money', 'movies', 'music', 'photography', 'politics', 'programming', 'travel',
            'relationships', 'religion', 'science', 'sports', 'technology', 'tv_shows', 'collecting', 'vehicles'
        ]

        for key, _ in self.instance.vocabDictBuilder().items():
            key_arr.append(key)

        assert key_arr == expected_key_arr
        