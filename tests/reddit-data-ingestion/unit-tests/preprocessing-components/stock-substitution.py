import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing import substitute_stock

class TestStockSubstitution:
    def setup_method(self):
        self.stock_text_no_prefix = "I want to buy AAPL today"
        self.stock_test_prefix = "$AMZN is a good deal!"
        self.stock_test_lowercase = "$amzn is a good deal!"
    
    def test_stock_no_prefix(self):
        test_text = self.stock_text_no_prefix
        result = substitute_stock.replaceText(test_text)

        assert result == "I want to buy [stock] today"

    def test_stock_with_prefix(self):
        test_text = self.stock_test_prefix
        result = substitute_stock.replaceText(test_text)

        assert result == "[stock] is a good deal!"
    
    def test_lowercase(self):
        test_text = self.stock_test_lowercase
        result = substitute_stock.replaceText(test_text)

        assert result == "$amzn is a good deal!"
