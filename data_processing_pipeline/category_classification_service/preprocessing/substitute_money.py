import re    

class ReplaceText:
    def __init__(self):
        self.currency_symbols = r'[$€¥£₹]'
        self.currency_words = r'dollars?|bucks?|cents?|cad?|yen?|euros?'
        self.magnitude_words = r'billions?|bn|b(?!ucks)|millions?|m|thousands?|k'

    def numerical(self, rawtext):
        pattern = (
            rf"(?=(?:.*{self.currency_symbols}|.*\b(?:{self.currency_words})\b))" # look ahead condition
            rf"{self.currency_symbols}?\s?"
            r"\d{1,3}(?:,\d{3})*(?:\.\d+)?\s?"
            rf"{self.currency_symbols}?\s?"
            rf"(?:{self.magnitude_words})?\s?"
            rf"(?:{self.currency_words})?"
        )

            #money_pattern = re.compile(r'(?=(?:.*[$€¥£₹]|.*\b(?:dollars?|bucks?|cents?)\b))[$€¥£₹]?\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?\s?[$€¥£₹]?\s?(?:billions?|bn|b(?!ucks)|thousands?|k|millions?|m)?\s?(?:dollars?|bucks?|cents?)?')
        money_pattern = re.compile(pattern, re.IGNORECASE)
            
        return money_pattern.sub(' [money]', rawtext)
    
    def words(self, rawtext):
        # substitute word form of money
        return rawtext
        