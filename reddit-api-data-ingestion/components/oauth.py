import requests, requests.auth, os
from dotenv import load_dotenv

class Oauth:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("Reddit-Api-Client-ID")
        self.client_secret = os.getenv("Reddit-Api-Client-Secret")
        self.account_username = os.getenv("Reddit-Account-Username")
        self.account_password = os.getenv("Reddit-Account-Password")
    def get_Oauth_token(self):
        client_auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        post_data = {"grant_type": "password", "username": self.account_username, "password": self.account_password}
        headers = {"User-Agent": "ChangeMeClient/0.1 by YourUsername"}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
        token = response.json()
        OauthToken = token['access_token']
        return OauthToken

Oauth_token = Oauth()
