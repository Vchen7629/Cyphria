from src.middleware.topic_category_mapping import get_category_for_topic
import pytest

@pytest.mark.parametrize(argnames="topic", argvalues=["GPU", "gPu", "  GPU   "])
def test_valid_input_topics(topic: str) -> None:
    """Fetching a category for a valid category should return the category string"""
    assert get_category_for_topic(topic) == "Computing"

@pytest.mark.parametrize(argnames="topic", argvalues=[None, "", "  "])
def test_invalid_input_topics(topic: str | None) -> None:
    """Trying to fetch category for invalid topic (None, empty string, whitespace) should return None"""
    assert get_category_for_topic(topic) == None # type: ignore

def test_non_existant_topic() -> None:
    """Trying to fetch category for a non existant topic should return None"""
    assert get_category_for_topic("jaajaja") == None