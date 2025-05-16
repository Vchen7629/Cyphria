import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing import remove_noise

class TestBracketFilter:
    def setup_method(self):
        self.instance = remove_noise.removeNoise()

    def test_filter_brace(self):
        test_text = "This is a{} test sentence{, please check} if this works."
        result = self.instance.removeBrackets(test_text)

        assert result == "This is a test sentence, please check if this works."

    def test_filter_square_bracket(self):
        test_text = "This is a[] test sentence[, please check] if this works."
        result = self.instance.removeBrackets(test_text)

        assert result == "This is a test sentence, please check if this works."

    def test_filter_parenthesis(self):
        test_text = "This is a() test sentence(, please check) if this works."
        result = self.instance.removeBrackets(test_text)

        assert result == "This is a test sentence, please check if this works."
    
    def test_filter_all(self):
        test_text = "This is a() test[] sentence(, please check) if{} this works."
        result = self.instance.removeBrackets(test_text)

        assert result == "This is a test sentence, please check if this works."

    def test_filter_recursive(self):
        test_text = "This is a test[({})] sentence, please check) if this works."
        result = self.instance.removeBrackets(test_text)

        assert result == "This is a test sentence, please check if this works."
