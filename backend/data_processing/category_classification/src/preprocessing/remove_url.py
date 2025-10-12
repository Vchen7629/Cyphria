import re


# This function checks the reddit post for url links and removes them
def remove_url(rawdata: str) -> str:
    url_pattern = re.compile(r"https?://\S+|www\.\S+")
    result = url_pattern.sub("", rawdata)

    return result
