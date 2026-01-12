from src.preprocessing.demojify import demojify

def test_demojify_emoji() -> None:
    """Emoji should be properly demojified to the text version"""
    result = demojify("This dog is very cute 😊")

    assert result == "This dog is very cute [smiling_face_with_smiling_eyes]"

def test_emoji_in_text() -> None:
    """Emoji in between text with no space should still be demojified to text version"""
    result = demojify("This dog😊go is very cute")

    assert result == "This dog[smiling_face_with_smiling_eyes]go is very cute"

def test_no_emoji() -> None:
    """It should return original text if no emoji"""
    result = demojify("This doggo is very cute")

    assert result == "This doggo is very cute"