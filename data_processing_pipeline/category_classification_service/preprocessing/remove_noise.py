import re, os

class removeNoise:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        stopword_path = os.path.join(script_dir, '..', 'datasets', 'stopwords.txt')

        with open(stopword_path, 'r', encoding='utf-8') as f:
            self.stopword_instance = set(line.strip() for line in f if line.strip())
        
    def removeURL(self, rawdata): 
        url_pattern = re.compile(r'https?://\S+|www\.\S+')

        result = url_pattern.sub("", rawdata)

        return result
    
    def removeBrackets(self, rawdata):
        bracket_pattern = re.compile(r'\[|\]|{|}|\(|\)')
        result = bracket_pattern.sub("", rawdata)

        return result

    def removeStopWords(self, rawData):
        tokenized_text = rawData.split()

        filtered_text = [word for word in tokenized_text if word.lower() not in self.stopword_instance]

        new_clean_text = ' '.join(filtered_text)

        return new_clean_text
    
    def removeOldRedditPosts(self, rawData):
        if "post contains content supported old Reddit" not in rawData:
            return True
        else:
            return False
        
    def removeCommas(self, rawdata):
        comma_pattern = re.compile(r',')
        result = comma_pattern.sub("", rawdata)
        
        return result
    
