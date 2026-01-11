from src.preprocessing.url_remover import remove_url
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))


def test_post_regular() -> None:
    """Regular url should be removed"""
    text = "Come to www.amazon.com to see new deals!"
    result = remove_url(text)

    assert result == "Come to  to see new deals!"


def test_no_www() -> None:
    """No prefix url should still be removed"""
    text = "Come to amazon.com to see new deals!"
    result = remove_url(text)

    assert result == "Come to  to see new deals!"


def test_no_com() -> None:
    """No .com ending in url should still be removed"""
    text = "Come to www.amazon to see new deals!"
    result = remove_url(text)

    assert result == "Come to  to see new deals!"


def test_http() -> None:
    """https prefix url should be removed"""
    text = "Come to https://www.amazon.com to see new deals!"
    result = remove_url(text)

    assert result == "Come to  to see new deals!"

