import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing.build_vocab import multi_file_source

class TestFunction:
    def setup_method(self):
        self.instance = multi_file_source.VocabLoader("lexicon_datasets", "politics")
        self.file_names = ['party.txt', 'politician.txt', 'terms.txt']

    def test_array_length(self) -> bool:
        array = self.instance.combineVocab(self.file_names)

        assert len(array) == 221

    def test_array_all_str(self) -> bool:
        array = self.instance.combineVocab(self.file_names)

        assert all(isinstance(item, str) for item in array) == True