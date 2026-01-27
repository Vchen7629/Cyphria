import emoji
import re


def demojify(comment_text: str) -> str:
    """
    Helper function for converting emoji characters into plain text

    Args:
        comment_text: raw comment text that may or may not have emojis

    Returns:
        demojized_text_with_bracket: comment text with emojis converted to
                                    a string with brackets around it
    """
    demojized: str = emoji.demojize(comment_text)

    # add bracket delimiter around demojized text to seperate it
    demojized_text_with_bracket: str = re.sub(r":([a-zA-Z0-9_]+):", r"[\1]", demojized)

    return demojized_text_with_bracket
