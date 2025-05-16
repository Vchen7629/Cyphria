from langdetect import detect

def isEnglish(text):
    try:
        combined_text = text.get('body', '')
        return detect(combined_text) == 'en'
    except:
        return False
    