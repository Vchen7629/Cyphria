import praw
from prawcore.exceptions import Forbidden


# Python Function to handle data fetching using PRAW
def get_posts(reddit_client: praw.Reddit, subreddit: str) -> list[praw.models.Submission]:
    try:
        return list(reddit_client.subreddit(subreddit).new(limit=20))
    except Forbidden as e:
        print(
            "Error fetching",
            e,
        )
