from src.preprocessing.extract_pairs import extract_pairs
from src.core.types import UnprocessedComment
from datetime import datetime, timezone

def test_normal() -> None:
    """Test with valid comment body and product list"""
    unprocessed_comment = UnprocessedComment(
        comment_id="idk123",
        comment_body="This is test post about cats and dogs",
        category="Animal",
        detected_products=["cats", "dogs"],
        created_utc=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc) 
    )

    result = extract_pairs(unprocessed_comment)

    assert result == [
        ("idk123", "This is test post about cats and dogs", "Animal", "cats", datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)),
        ("idk123", "This is test post about cats and dogs", "Animal", "dogs", datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)),
    ]


def test_no_comment_body() -> None:
    """No comment body in value edge case"""
    unprocessed_comment = UnprocessedComment(
        comment_id="idk123",
        comment_body="",
        category="Animal",
        detected_products=["cats", "dogs"],
        created_utc=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc) 
    )

    result = extract_pairs(unprocessed_comment)

    assert result == []


def test_no_detected_products() -> None:
    """No detected products list in value edge case"""
    unprocessed_comment = UnprocessedComment(
        comment_id="idk123",
        comment_body="This is test post about cats and dogs",
        category="Animal",
        detected_products=[],
        created_utc=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    result = extract_pairs(unprocessed_comment)

    assert result == []

def test_no_comment_body_or_detected_products() -> None:
    """No comment body or detected_product list edge case"""
    unprocessed_comment = UnprocessedComment(
        comment_id="idk123",
        comment_body="",
        category="Animal",
        detected_products=[],
        created_utc=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc) 
    )

    result = extract_pairs(unprocessed_comment)

    assert result == []
