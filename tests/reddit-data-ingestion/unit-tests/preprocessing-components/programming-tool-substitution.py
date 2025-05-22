import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing import lexicon_substitution

class TestProgrammingToolSubstitution:
    def setup_method(self):
        self.instance = lexicon_substitution.SubTextInRedditPosts()

        self.lowercase = "I want to learn javascript"
        self.uppercase = "I used REACT.js, MONGODB, and GOLANG to create that website!"

    def test_lowercase(self):
        test_text = self.lowercase
        result = self.instance.replaceProgrammingTools(test_text)

        assert result == "I want to learn [programmingtool]"
    
    def test_uppercase(self):
        test_text = self.uppercase
        result = self.instance.replaceProgrammingTools(test_text)

        assert result == "I used [programmingtool] [programmingtool] and [programmingtool] to create that website!"

