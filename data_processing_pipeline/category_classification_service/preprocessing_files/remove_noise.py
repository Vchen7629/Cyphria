import re, os

class removeNoise:
    def __init__(self) -> None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        stopword_path = os.path.join(script_dir, '..', 'datasets', 'stopwords.txt')

        with open(stopword_path, 'r', encoding='utf-8') as f:
            self.stopword_instance = set(line.strip() for line in f if line.strip())
        
    def url(self, rawdata: str) -> str: 
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        result = url_pattern.sub("", rawdata)

        return result
    
    def brackets(self, rawdata: str) -> str:
        bracket_pattern = re.compile(r'\[|\]|{|}|\(|\)')
        result = bracket_pattern.sub("", rawdata)

        return result

    def stopWords(self, rawData: str) -> str:
        tokenized_text = rawData.split()
        filtered_text = [word for word in tokenized_text if word.lower() not in self.stopword_instance]
        new_clean_text = ' '.join(filtered_text)

        return new_clean_text
    
    def oldRedditPosts(self, rawData: str) -> bool:
        if "post contains content supported old Reddit" not in rawData:
            return True
        else:
            return False
        
    def punctuation(self, rawdata: str) -> str:
        comma_pattern = re.compile(r',|\.')
        result = comma_pattern.sub("", rawdata)
        
        return result
    