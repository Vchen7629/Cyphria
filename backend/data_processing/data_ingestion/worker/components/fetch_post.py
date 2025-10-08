import praw  # type: ignore
from prawcore.exceptions import Forbidden  # type: ignore
from ..middleware.logger import StructuredLogger


# Python Function to handle data fetching using PRAW
def get_posts(
    reddit_client: praw.Reddit, subreddit: str, logger: StructuredLogger
) -> list[praw.models.Submission] | None:
    try:
        return list(reddit_client.subreddit(subreddit).new(limit=20))
    except Forbidden as e:
        logger.error(event_type="RedditApi", message=f"Error fetching posts from reddit: {e}")

        return None
