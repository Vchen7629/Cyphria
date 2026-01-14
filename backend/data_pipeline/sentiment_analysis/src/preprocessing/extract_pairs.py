from src.core.types import UnprocessedComment
from datetime import datetime

def extract_pairs(unprocessed_comment: UnprocessedComment) -> list[tuple[str, str, str, datetime]]:
    """
    Create enriched pairs from an unprocessed comment containing all metadata
    needed for sentiment analysis and database insertion.

    Args:
        unprocessed_comment: UnprocessedComment Pydantic model containing comment data

    Returns:
        A list of tuples: (comment_id, comment_body, product_name, created_utc)
        Returns empty list if comment_body is empty or no products detected
    """
    comment_text: str = unprocessed_comment.comment_body.strip()
    product_list: list[str] = unprocessed_comment.detected_products

    if not comment_text or not product_list:
        return []

    return [
        (unprocessed_comment.comment_id, comment_text, product, unprocessed_comment.created_utc)
        for product in product_list
    ]
