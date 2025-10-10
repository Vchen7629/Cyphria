from langdetect import detect, LangDetectException, DetectorFactory  # type: ignore

DetectorFactory.seed = 0  # detect language consistent


# Python function to make sure only english posts get processed
def detect_english(text: str) -> str | None:
    try:
        if not text.strip():
            return None
        return detect(text)
    except LangDetectException:
        return None
