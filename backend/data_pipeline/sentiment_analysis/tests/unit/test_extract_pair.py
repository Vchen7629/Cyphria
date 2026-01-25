from datetime import datetime
from datetime import timezone
from src.api.schemas import UnprocessedComment
from src.preprocessing.extract_pairs import extract_pairs
import pytest


def test_normal() -> None:
    """Test with valid comment body and product list"""
    unprocessed_comment = UnprocessedComment(
        comment_id="idk123",
        comment_body="This is test post about cats and dogs",
        product_topic="Animal",
        detected_products=["cats", "dogs"],
        created_utc=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc) 
    )

    result = extract_pairs(unprocessed_comment)

    assert result == [
        ("idk123", "This is test post about cats and dogs", "Animal", "cats", datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)),
        ("idk123", "This is test post about cats and dogs", "Animal", "dogs", datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)),
    ]

@pytest.mark.parametrize(argnames="comment_body,detected_products", argvalues=[
    ("", ["cats", "dogs"]), # no comment body
    ("This is test post", []), # no detected products list
    ("", []) # both no comment body and no detected products list
])
def test_invalid_comment_params(comment_body: str, detected_products: list[str]) -> None:
    """No comment body in value edge case"""
    unprocessed_comment = UnprocessedComment(
        comment_id="idk123",
        comment_body=comment_body,
        product_topic="Animal",
        detected_products=detected_products,
        created_utc=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc) 
    )

    result = extract_pairs(unprocessed_comment)

    assert result == []