from datetime import datetime, timezone
from praw.models import Comment
from src.api.schemas import RedditComment


def extract_relevant_fields(comment: Comment, detected_products: list[str]) -> RedditComment:
    """
    Extract relevant data fields from reddit comment to
    reduce amount of data being sent to data pipeline

    Args:
        comment: PRAW reddit comment object containing all data fields
        detected_products: List of product strings found in the comment text

    Returns
        comment_id: the comment unique id
        comment_body: comment text
        subreddit: the subreddit the post is from
        timestamp: timestamp converted from posix timestamp to utc
        score: total score of the reddit comment (upvotes - downvotes)
        author: the comment poster name
        post_id: id linking each comment to the parent reddit post
    """
    return RedditComment(
        comment_id=comment.id,
        comment_body=comment.body,
        subreddit=comment.subreddit.display_name,
        detected_products=detected_products,
        timestamp=datetime.fromtimestamp(comment.created_utc, tz=timezone.utc),
        score=comment.score,
        author=comment.author.name,
        post_id=comment.link_id,
    )
