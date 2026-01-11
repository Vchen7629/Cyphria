import json
from src.preprocessing.extract_pairs import extract_pairs


# Mocking Kafka Message
class MockMessage:
    def __init__(self, value: dict):
        self._value = json.dumps(value).encode("utf-8")

    def value(self) -> bytes:
        return self._value


# Happy path: expected behavior
def test_normal() -> None:
    msg = MockMessage(
        value={"body": "This is test post about cats and dogs", "keywords": ["cats", "dogs"]}
    )

    result = extract_pairs(msg)

    assert result == [
        ("This is test post about cats and dogs", "cats"),
        ("This is test post about cats and dogs", "dogs"),
    ]


# edge case: no body in value
def test_no_body() -> None:
    msg = MockMessage(value={"body": "", "keywords": ["cats", "dogs"]})

    result = extract_pairs(msg)

    assert result == []


# edge case: no keywords in value
def test_no_keywords() -> None:
    msg = MockMessage(value={"body": "This is test post about cats and dogs", "keywords": []})

    result = extract_pairs(msg)

    assert result == []


# edge case: no keywords and body in value
def test_no_keywords_body() -> None:
    msg = MockMessage(value={"body": "", "keywords": []})

    result = extract_pairs(msg)

    assert result == []
