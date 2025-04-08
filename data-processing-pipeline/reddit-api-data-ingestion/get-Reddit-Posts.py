from oauth import Oauth
import requests, requests.auth
from components.reddit_api_producer import r_producer
from components.post_filtering import filter

class RedditPosts:
    def __init__(self):
        Oauth_init = Oauth()
        self.Oauth_Token = Oauth_init.get_Oauth_token()
        self.last_post_name = None
    
    def GetPosts(self):
        headers = {"Authorization": "Bearer " + self.Oauth_Token, "User-Agent": "ChangeMeClient/0.1 by YourUsername"}
        params = {"limit": 100, "lang": "en"}
        
        if self.last_post_name:
            params["after"] = self.last_post_name
            
        response = requests.get("https://oauth.reddit.com/r/all/new", params=params,headers=headers)
        if response.status_code == 200:
            res = response.json()
            english_only = []
            
            if filter.postExists(res) == True:
                if res['data']['children'] and 'data' in res['data']['children'][-1]:
                    self.last_post_name = res['data']['children'][-1]['data']['name']
                for post in res['data']['children']:
                    post_data = filter.Extract_Relevant_Data(post)
                    
                    if post_data and (post_data['body']) and (post_data['title'] != "What is this?"):
                        if filter.isEnglish(post_data):
                            english_only.append(post_data)
                            #subreddit = post_data['subreddit']
                            
            
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
            
            r_producer.Send_Message(english_only)
            
            print("english only: ", english_only)

            return english_only
        
        elif response.status_code == 401:
            print("Refreshing token...")
            Oauth_init = Oauth()
            self.Oauth_Token = Oauth_init.get_Oauth_token()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
           
posts = RedditPosts()

if __name__ == "__main__":
    for i in range(1):
        posts.GetPosts()
    print("Closing producer.")
    r_producer.producer.close()