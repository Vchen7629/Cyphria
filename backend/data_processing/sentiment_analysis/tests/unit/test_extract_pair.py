import json
from src.preprocessing.extract_pairs import extract_pairs

# Mocking Kafka Message
class MockMessage:
    def __init__(self, key: str, value: dict):
        self._key = key.encode("utf-8")
        self._value = json.dumps(value).encode("utf-8")
    
    def key(self) -> bytes:
        return self._key
    
    def value(self) -> bytes:
        return self._value

# Happy path: expected behavior
def test_normal() -> None: 
    msg = MockMessage(
        key="abc123",
        value={
            "body": "This is test post about cats and dogs",
            "keywords": ["cats", "dogs"]
        }
    )

    result = extract_pairs(msg)

    assert result == [
        ("abc123", "This is test post about cats and dogs", "cats"),
        ("abc123", "This is test post about cats and dogs", "dogs"),
    ]

# edge case: no body in value
def test_no_body() -> None: 
    msg = MockMessage(
        key="abc123",
        value={
            "body": "",
            "keywords": ["cats", "dogs"]
        }
    )

    result = extract_pairs(msg)

    assert result == []

# edge case: no keywords in value
def test_no_keywords() -> None: 
    msg = MockMessage(
        key="abc123",
        value={
            "body": "This is test post about cats and dogs",
            "keywords": []
        }
    )

    result = extract_pairs(msg)

    assert result == []

# edge case: no keywords and body in value
def test_no_keywords_body() -> None: 
    msg = MockMessage(
        key="abc123",
        value={
            "body": "",
            "keywords": []
        }
    )

    result = extract_pairs(msg)

    assert result == []