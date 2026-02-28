from src.preprocessing.demojify import demojify
from src.preprocessing.url_remover import remove_url
import pytest


@pytest.mark.parametrize(
    argnames="original_sentence,expected",
    argvalues=[
        ("This dog is very cute 😊", "This dog is very cute [smiling_face_with_smiling_eyes]"),
        ("This dog😊go is very cute", "This dog[smiling_face_with_smiling_eyes]go is very cute"),
        ("This doggo is very cute", "This doggo is very cute"),  # no emoji just returns original
    ],
)
def test_demojify_emoji(original_sentence: str, expected: str) -> None:
    """Emoji should be properly demojified to the text version"""
    assert demojify(original_sentence) == expected


@pytest.mark.parametrize(
    argnames="original_sentence,expected",
    argvalues=[
        ("Come to www.amazon.com to see new deals!", "Come to  to see new deals!"),
        ("Come to amazon.com to see new deals!", "Come to  to see new deals!"),
        ("Come to www.amazon to see new deals!", "Come to  to see new deals!"),
    ],
)
def test_remove_url(original_sentence: str, expected: str) -> None:
    """Regular url should be removed"""
    assert remove_url(original_sentence) == expected
