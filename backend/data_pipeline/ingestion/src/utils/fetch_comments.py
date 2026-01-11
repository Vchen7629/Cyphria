from prawcore.exceptions import PrawcoreException  # type: ignore
from ..core.logger import StructuredLogger
from praw.models import Submission, Comment

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
        return post.comments.list()
    except PrawcoreException as e:
        logger.error(
            event_type="RedditApi",
            message=f"Error fetching comments for post {post.id}: {e}"
        )
        return []