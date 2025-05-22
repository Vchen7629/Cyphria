import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service.preprocessing import substitute_money

class TestMoneySubstitution:
    def setup_method(self):
        self.instance = substitute_money.ReplaceText()

        self.dollar_text = "I have $5 dollars!"
        self.money_with_decimal_text = "I have $5.00 bucks!"
        self.reversed_money_text = "I have 5$ dollar!"
        self.no_currency_symbol = "I have 500,000!"
        self.money_with_suffix = "I have 600b dollars"

    def test_dollar_text(self):
        test_text = self.dollar_text
        result = self.instance.numerical(test_text)

        assert result == "I have  [money]!"

    def test_money_with_decimal(self):
        test_text = self.money_with_decimal_text
        result = self.instance.numerical(test_text)

        assert result == "I have  [money]!"
    
    def test_reversed_money(self):
        test_text = self.reversed_money_text
        result = self.instance.numerical(test_text)

        assert result == "I have [money]!"

    def test_no_currency_symbol(self):
        test_text = self.no_currency_symbol
        result = self.instance.numerical(test_text)

        assert result == "I have 500,000!"

    def test_money_with_suffix(self):
        test_text = self.money_with_suffix
        result = self.instance.numerical(test_text)

        assert result == "I have [money]"
    