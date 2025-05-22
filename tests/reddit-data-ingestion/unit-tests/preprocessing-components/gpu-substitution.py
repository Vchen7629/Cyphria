import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing import lexicon_substitution

class TestGPUSubstitution:
    def setup_method(self):
        self.instance = lexicon_substitution.SubTextInRedditPosts()

        self.lowercase = "I want a new geforce rtx 5090!"
        self.uppercase = "The new Radeon RX 7600 is out"

    def test_lowercase(self):
        test_text = self.lowercase
        result = self.instance.replaceGpuNames(test_text)

        assert result == "I want a new [gpu]!"

    def test_uppercase(self):
        test_text = self.uppercase
        result = self.instance.replaceGpuNames(test_text)

        assert result == "The new [gpu] is out"
