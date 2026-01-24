from datetime import datetime
from datetime import timezone
from datetime import timedelta
from praw.models import Submission
from prawcore.exceptions import Forbidden  # type: ignore
from src.core.logger import StructuredLogger
import praw  # type: ignore

def fetch_post_delayed(
    reddit_client: praw.Reddit, subreddit: str, logger: StructuredLogger, delay_hours: int = 24
) -> list[Submission] | None:
    """
    Fetch reddit posts that are 24-48 hours old using PRAW.

    Uses a delay to ensure posts have accumulated most of their comments.
    Posts are fetched from the time window: [48 hours ago, 24 hours ago]

    Args:
        reddit_client: Authenticated PRAW Reddit instance
        subreddit: Subreddit name to fetch from
        logger: Structured logger instance
        delay_hours: Hours to delay (default 24). Posts fetched are 24-48 hours old.

    Returns:
        List of submissions or None if error occurs
    """
    subreddit_obj = reddit_client.subreddit(subreddit)

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=delay_hours + 24)  # 48 hours ago
    end_time = now - timedelta(hours=delay_hours)  # 24 hours ago

    posts: list[Submission] = []
    try:
        for post in subreddit_obj.new(limit=1000):
            # Fix: Add timezone to post_time for accurate comparison
            post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)

            if post_time > end_time:
                continue  # Too new, skip
            if post_time < start_time:
                # Posts are sorted newest->oldest, so we can break early
                break

            posts.append(post)
    except Forbidden as e:
        logger.error(event_type="RedditApi", message=f"Error fetching posts from reddit: {e}")
        return None

    return posts
