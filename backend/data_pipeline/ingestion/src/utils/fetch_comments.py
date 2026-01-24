from typing import cast
from praw.models import Comment
from praw.models import Submission
from prawcore.exceptions import PrawcoreException  # type: ignore
from src.core.logger import StructuredLogger

def fetch_comments(post: Submission, logger: StructuredLogger, limit: int | None = None) -> list[Comment]:
    """
    Fetch all comments from a reddit post

    Args:
        post: PRAW Submission object (reddit post)
        logger: Structured logger instance
        limit: Max number of MoreComments instances to replace
               None = replace all (fetches all comments including nested ones)

    Returns:
        List of Comment objects
    
    
    """
    try:
        post.comments.replace_more(limit=limit)

        # flatten comment forest into list
        # After replace_more(), only Comment objects remain (MoreComments are replaced)
        return cast(list[Comment], post.comments.list())
    except PrawcoreException as e:
        logger.error(
            event_type="RedditApi",
            message=f"Error fetching comments for post {post.id}: {e}"
        )
        return []