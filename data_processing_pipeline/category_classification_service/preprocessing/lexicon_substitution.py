import re, os
import pandas as pd

class SubTextInRedditPosts:
    def __init__(self):
        self.currency_symbols = r'[$€¥£₹]'
        self.currency_words = r'dollars?|bucks?|cents?|cad?|yen?|euros?'
        self.magnitude_words = r'billions?|bn|b(?!ucks)|millions?|m|thousands?|k'

        base_dir = os.path.dirname(os.path.abspath(__file__))

        stock_data_txt_path = os.path.join(base_dir, '..', 'datasets', 'stock_names.txt')
        stock_names_df = pd.read_csv(stock_data_txt_path, header=None)
        programming_tools_data_txt_path = os.path.join(base_dir, '..', 'datasets', 'programming_tools.txt')
        programming_tools_df = pd.read_csv(programming_tools_data_txt_path, header=None)
        gpu_names_txt_path = os.path.join(base_dir, '..', 'datasets', 'gpu_names.txt')
        vehicle_brands_txt_path = os.path.join(base_dir, '..', 'datasets', 'vehicle_brands.txt')

        # converting to set for O(1) lookup
        self.stock_names = set(stock_names_df[0].str.strip())
        self.programming_tools = set(w.lower() for w in programming_tools_df[0].str.strip())

        with open(gpu_names_txt_path, 'r') as f:
            gpu_names = [line.strip() for line in f if line.strip()]
            escaped_gpu_names = [re.escape(name) for name in gpu_names]
            self.gpu_pattern = r'\b(?:' + '|'.join(escaped_gpu_names) + r')\b'

        with open(vehicle_brands_txt_path, 'r') as f:
            vehicle_brands = [line.strip() for line in f if line.strip()]
            escaped_vehicle_brands = [re.escape(brand) for brand in vehicle_brands]
            self.vehicle_brand_pattern = r'\b(?:' + '|'.join(escaped_vehicle_brands) + r')\b'

    def replaceAge(self, rawtext):
        age_pattern = re.compile(r'\b\d{1,3}\s?(months old|days old|years old|yo|yr old|yrs old|y/o|m|f)\b')
        return age_pattern.sub('[age]', rawtext, re.IGNORECASE)

    def replaceNumericalMoney(self, rawtext):
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
    
    def replaceStockName(self, rawtext):
        tokenized_text = rawtext.split()
        dataset = self.stock_names
        new_sentence = []

        for word in tokenized_text:
            if word in dataset or (word.startswith('$') and word[1:] in dataset):
                new_sentence.append('[stock]')
            else:
                new_sentence.append(word)

        return ' '.join(new_sentence)
    
    def replaceProgrammingTools(self, rawtext):
        tokenized_text = rawtext.split()
        dataset = self.programming_tools
        new_sentence = []

        for word in tokenized_text:
            clean_word = word.strip('.,!?') 
            if clean_word.lower() in dataset:
                new_sentence.append('[programmingtool]')
            else:
                new_sentence.append(word)
                
        return ' '.join(new_sentence)
    
    def replaceGpuNames(self, rawtext):
        gpu_pattern = self.gpu_pattern
        pattern = re.compile(gpu_pattern, flags=re.IGNORECASE)

        return pattern.sub('[gpu]', rawtext)
    
    def replaceVehicleBrands(self, rawtext):
        vehicle_brand_pattern = self.vehicle_brand_pattern
        pattern = re.compile(vehicle_brand_pattern, flags=re.IGNORECASE)

        return pattern.sub('[vehicleBrand]', rawtext)
    
    def replaceClassNames(self, rawtext):
        # regex matching for a list of class abreviations like CSE, PSY, etc followed by 3 numbers like 100 or 234
        
