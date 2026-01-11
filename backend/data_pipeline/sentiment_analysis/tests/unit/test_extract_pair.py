import json
from src.preprocessing.extract_pairs import extract_pairs


# Mocking Kafka Message
class MockMessage:
    def __init__(self, value: dict[str, str | list[str]]) -> None:
        self._value = json.dumps(value).encode("utf-8")

    def value(self) -> bytes:
        return self._value


def test_normal() -> None:
    """mock message with the body and product list"""
    msg = MockMessage(
        value={"comment_body": "This is test post about cats and dogs", "detected_products": ["cats", "dogs"]}
    )

    result = extract_pairs(msg.value().decode("utf-8"))

    assert result == [
        ("This is test post about cats and dogs", "cats"),
        ("This is test post about cats and dogs", "dogs"),
    ]

def test_no_comment_body() -> None:
    """No comment body in value edge case"""
    msg = MockMessage(value={"comment_body": "", "detected_products": ["cats", "dogs"]})

    result = extract_pairs(msg.value().decode("utf-8"))

    assert result == []


def test_no_detected_products() -> None:
    """No detected products list in value edge case"""
    msg = MockMessage(value={"comment_body": "This is test post about cats and dogs", "detected_products": []})

    result = extract_pairs(msg.value().decode("utf-8"))

    assert result == []


def test_no_comment_body_or_detected_products() -> None:
    """No comment body or detected_product list in mock message edge case"""
    msg = MockMessage(value={"comment_body": "", "detected_products": []})

    result = extract_pairs(msg.value().decode("utf-8"))

    assert result == []
