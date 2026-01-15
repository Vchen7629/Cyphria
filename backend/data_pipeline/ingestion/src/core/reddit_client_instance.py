from dotenv import load_dotenv
import praw  # type: ignore
from src.core.settings_config import Settings

settings = Settings()

def createRedditClient() -> praw.Reddit:
    """
    Creates an instance of reddit client required for praw

    Returns:
        reddit: instance of praw reddit client
    """
    reddit = praw.Reddit(
        client_id=settings.Reddit_Api_Client_ID,
        client_secret=settings.Reddit_Api_Client_Secret,
        username=settings.Reddit_Account_Username,
        password=settings.Reddit_Account_Password,
        user_agent="ChangeMeClient/0.1 by u/ZephyrusDragon",
    )

    return reddit
