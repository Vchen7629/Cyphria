import os, praw
from dotenv import load_dotenv


class Auth:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("Reddit-Api-Client-ID")
        self.client_secret = os.getenv("Reddit-Api-Client-Secret")
        self.account_username = os.getenv("Reddit-Account-Username")
        self.account_password = os.getenv("Reddit-Account-Password")

    def createRedditClient(self):
        reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            password=self.account_password,
            user_agent="ChangeMeClient/0.1 by u/ZephyrusDragon",
            username=self.account_username
        )

        return reddit
        

Oauth_token = Auth()
