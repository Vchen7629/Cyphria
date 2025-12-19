import emoji
import re

def demojify(text: str) -> str:
    demojized = emoji.demojize(text)
    add_bracket = re.sub(r":([a-zA-Z0-9_]+):", r"[\1]", demojized)

    return add_bracket
