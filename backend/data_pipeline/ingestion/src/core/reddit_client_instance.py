from src.core.settings_config import Settings
import praw

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
