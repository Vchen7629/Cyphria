from src.middleware.topic_category_mapping import get_topics_for_category
import pytest


@pytest.mark.parametrize(
    argnames="category", argvalues=["COMPUTING", "comPuTING", "  COMPUTING   "]
)
def test_valid_input_category(category: str) -> None:
    """Fetching topics for a valid category should return the matching topic list"""
    assert get_topics_for_category(category) == [
        "CPU",
        "GPU",
        "LAPTOP",
        "MECHANICAL KEYBOARD",
        "MONITOR",
    ]


@pytest.mark.parametrize(argnames="category", argvalues=[None, "", "  "])
def test_invalid_input_category(category: str | None) -> None:
    """Trying to fetch topics for invalid category (None, empty string, whitespace) should return empty list"""
    assert get_topics_for_category(category) == []  # type: ignore


def test_non_existant_category() -> None:
    """Trying to fetch topics for a non existant category should return None"""
    assert get_topics_for_category("jaajaja") == []
