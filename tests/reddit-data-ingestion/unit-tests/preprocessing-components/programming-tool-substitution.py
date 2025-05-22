import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing import substitute_prog_tools

class TestProgrammingToolSubstitution:
    def setup_method(self):
        self.lowercase = "I want to learn javascript"
        self.uppercase = "I used REACT.js, MONGODB, and GOLANG to create that website!"

    def test_lowercase(self):
        test_text = self.lowercase
        result = substitute_prog_tools.replaceText(test_text)

        assert result == "I want to learn [programmingtool]"
    
    def test_uppercase(self):
        test_text = self.uppercase
        result = substitute_prog_tools.replaceText(test_text)

        assert result == "I used [programmingtool] [programmingtool] and [programmingtool] to create that website!"

