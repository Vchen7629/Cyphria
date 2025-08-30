from langdetect import detect

def isEnglish(text: str) -> bool:
    if detect(text) == 'en':
        return True
    else:
        return False
    