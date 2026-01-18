import praw  # type: ignore
from src.core.settings_config import Settings

settings: Settings = Settings()

def createRedditClient() -> praw.Reddit:
    """
    Creates an instance of reddit client required for praw

    Returns:
        reddit: instance of praw reddit client
    """
    reddit = praw.Reddit(
        client_id=settings.REDDIT_API_CLIENT_ID,
        client_secret=settings.REDDIT_API_CLIENT_SECRET,
        username=settings.REDDIT_ACCOUNT_USERNAME,
        password=settings.REDDIT_ACCOUNT_PASSWORD,
        user_agent="ChangeMeClient/0.1 by u/ZephyrusDragon",
    )

    return reddit
