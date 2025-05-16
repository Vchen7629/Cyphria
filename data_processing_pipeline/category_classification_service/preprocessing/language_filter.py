from langdetect import detect

def isEnglish(text):
    try:
        return detect(text) == 'en'
    except:
        return False
    