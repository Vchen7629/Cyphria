import re

def replaceText(rawtext):
    age_pattern = re.compile(r'\b\d{1,3}\s?(months old|days old|years old|yo|yr old|yrs old|y/o|m|f)\b')
    return age_pattern.sub('[age]', rawtext, re.IGNORECASE)