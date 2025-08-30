import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing import remove_noise

class TestUrlRemover:
    def setup_method(self):
        self.instance = remove_noise.removeNoise()

    def test_http_filtered(self):
        test_string = "This is a test string at http://www.google.com"
        result = self.instance.url(test_string)

        assert result == "This is a test string at "

    def test_https_filtered(self):
        test_string = "This is a test string at https://www.amazon.com"
        result = self.instance.url(test_string)

        assert result == "This is a test string at "

    def test_www_filtered(self):
        test_string = "This is a test string at www.spotify.com"
        result = self.instance.url(test_string)

        assert result == "This is a test string at "

    def test_no_url_not_filtered(self):
        test_string = "This is a test string"
        result = self.instance.url(test_string)

        assert result == "This is a test string"

    def test_url_middle_filtered(self):
        test_string = "This is a test string at http://www.google.com come watch"
        result = self.instance.url(test_string)

        assert result == "This is a test string at  come watch"

    def test_url_with_subpage_filtered(self):
        test_string = "This is a test string at http://www.google.com/a@23wdi come watch"
        result = self.instance.url(test_string)

        assert result == "This is a test string at  come watch"