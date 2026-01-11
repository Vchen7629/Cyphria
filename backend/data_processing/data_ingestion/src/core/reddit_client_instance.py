from dotenv import load_dotenv
import praw  # type: ignore
import os

load_dotenv()

def createRedditClient() -> praw.Reddit:
    """
    Creates an instance of reddit client required for praw

    Returns:
        reddit: instance of praw reddit client
    """
    reddit = praw.Reddit(
        client_id=os.getenv("Reddit-Api-Client-ID"),
        client_secret=os.getenv("Reddit-Api-Client-Secret"),
        username=os.getenv("Reddit-Account-Username"),
        password=os.getenv("Reddit-Account-Password"),
        user_agent="ChangeMeClient/0.1 by u/ZephyrusDragon",
    )

    return reddit
