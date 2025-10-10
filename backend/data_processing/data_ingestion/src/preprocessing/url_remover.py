import re


def remove_url(
    rawdata: str,
) -> str:
    url_pattern = re.compile(r"(?:https?://\S+|www\.\S+|\b\w+\.\w+\b)")

    result = url_pattern.sub(
        "",
        rawdata,
    )

    return result
