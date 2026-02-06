from typing import Optional
from langdetect import detect
from langdetect import DetectorFactory
from langdetect import LangDetectException
from src.utils.validation import validate_string

DetectorFactory.seed = 0  # detect language consistent


def detect_english(text: str) -> Optional[str]:
    """
    Checks the language of the text using langdetect.

    Args:
        text: the comment text we are checking language for

    Returns:
        the language of the detected text, or none if no text was supplied
    """
    if not validate_string(text, "text", raise_on_error=False):
        return None

    try:
        return detect(text)
    except LangDetectException:
        return None
