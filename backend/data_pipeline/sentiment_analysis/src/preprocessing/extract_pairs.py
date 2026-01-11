# Helper function for extracting Relevant fields for ABSA
import json

def extract_pairs(post_body: str) -> list[tuple[str, str]]:
    """
    Create pairs of (comment_body, product_name) for each detected product in the kafka message
    so we can run absa sentiment analysis on each product properly

    Args:
        post_body: the message body string we are extracting comment body and product name from

    Returns:
        a list of all the tuple pairs of (comment body, product_name)
    """
    postBody = json.loads(post_body)

    comment_text: str = postBody.get("comment_body", "").strip()
    product_list: list[str] = postBody.get("detected_products", [])

    if not comment_text or not product_list:
        return []

    batch = []

    for product in product_list:
        batch.append((comment_text, product))

    return batch
