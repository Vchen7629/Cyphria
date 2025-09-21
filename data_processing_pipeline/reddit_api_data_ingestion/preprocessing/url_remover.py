import re


def removeURL(
    rawdata,
    result="",
):
    url_pattern = re.compile(r"https?://\S+|www\.\S+")

    result = url_pattern.sub(
        "",
        rawdata,
    )

    return result
