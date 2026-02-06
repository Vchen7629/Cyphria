from src.utils.extract_subreddit_list import extract_subreddit_list
import pytest

@pytest.mark.parametrize(argnames="category", argvalues=["gpu", "  "])
def test_invalid_category_input(category: str) -> None:
    """Invalid category (non existant category, white space) should return empty list"""
    assert extract_subreddit_list(category) == []

@pytest.mark.parametrize(argnames="category", argvalues=["MOBILE", "moBILe", "  mobile  "])
def test_valid_category_input(category: str) -> None:
    """Category should still match for multiple valid inputs and return the subreddit list"""
    res = sorted(["Smartphones", "Android", "PickAnAndroidForMe", "iPhone", "AndroidTablets", "ipad", "tablets"])

    assert sorted(extract_subreddit_list(category)) == res