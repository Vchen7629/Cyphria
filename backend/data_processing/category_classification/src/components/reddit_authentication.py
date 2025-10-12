import os
import praw
from dotenv import (
    load_dotenv,
)


class Auth:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
    ):
        load_dotenv()
        self.client_id = os.getenv(client_id)
        self.client_secret = os.getenv(client_secret)
        self.account_username = os.getenv(username)
        self.account_password = os.getenv(password)

    def createRedditClient(
        self,
    ) -> praw.Reddit:
        reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            password=self.account_password,
            user_agent="ChangeMeClient/0.1 by u/ZephyrusDragon",
            username=self.account_username,
        )

        return reddit
