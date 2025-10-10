from src.preprocessing.url_remover import remove_url
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))


def test_post_regular():
    text = "Come to www.amazon.com to see new deals!"
    result = remove_url(text)

    assert result == "Come to  to see new deals!"


def test_no_www():
    text = "Come to amazon.com to see new deals!"
    result = remove_url(text)

    assert result == "Come to  to see new deals!"


def test_no_com():
    text = "Come to www.amazon to see new deals!"
    result = remove_url(text)

    assert result == "Come to  to see new deals!"


def test_http():
    text = "Come to https://www.amazon.com to see new deals!"
    result = remove_url(text)

    assert result == "Come to  to see new deals!"


def test_emojis():
    text = "Come to 🚀🔥🚀🔥 to see new deals!"
    result = remove_url(text)

    assert result == "Come to 🚀🔥🚀🔥 to see new deals!"
