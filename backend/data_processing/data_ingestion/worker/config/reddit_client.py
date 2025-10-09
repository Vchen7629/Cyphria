from dotenv import load_dotenv
import praw  # type: ignore
import os

load_dotenv()


# Sets up the reddit client with praw to be called
def createRedditClient() -> praw.Reddit:
    reddit = praw.Reddit(
        client_id=os.getenv("Reddit-Api-Client-ID"),
        client_secret=os.getenv("Reddit-Api-Client-Secret"),
        username=os.getenv("Reddit-Account-Username"),
        password=os.getenv("Reddit-Account-Password"),
        user_agent="ChangeMeClient/0.1 by u/ZephyrusDragon",
    )

    return reddit
