import re

def remove_url(comment_text: str) -> str:
    """
    Helper function to remove url from comment body text using regex

    Args:
        comment_text: comment text string that may or may not contain a url

    Returns:
        filtered: comment text string with url replaced by empty space
    """
    url_pattern = re.compile(r"(?:https?://\S+|www\.\S+|\b\w+\.\w+\b)")

    filtered: str = url_pattern.sub("", comment_text)

    return filtered
