import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing.file_loader import single_file_source

class TestFunction:
    def setup_method(self):
        self.instance = single_file_source.vocabLoader("lexicon_datasets", "science_terms.txt")

    def test_array_length(self) -> bool:
        array = self.instance

        assert len(array) == 58

    def test_array_all_str(self) -> bool:
        array = self.instance

        assert all(isinstance(item, str) for item in array) == True