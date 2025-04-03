from langdetect import detect

class PostFilter:
    def __init__(self):
        pass

    def isEnglish(self, text):
        try:
            combined_text = text.get('body', '')
            return detect(combined_text) == 'en'
        except:
            return False
    
    
filter = PostFilter()