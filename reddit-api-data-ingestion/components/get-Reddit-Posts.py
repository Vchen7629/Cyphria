from oauth import Oauth
import requests, requests.auth, os

class RedditPosts:
    def __init__(self):
        Oauth_init = Oauth()
        self.Oauth_Token = Oauth_init.get_Oauth_token()
        self.last_post_name = None
    
    def GetPosts(self):
        headers = {"Authorization": "Bearer " + self.Oauth_Token, "User-Agent": "ChangeMeClient/0.1 by YourUsername"}
        params = {"limit": 5, "lang": "en"}
        
        if self.last_post_name:
            params["after"] = self.last_post_name
            
        response = requests.get("https://oauth.reddit.com/r/all/new", params=params,headers=headers)
        if response.status_code == 200:
            res = response.json()
            extracted_data = []
            
            if 'data' in res and 'children' in res['data']:
                if res['data']['children'] and 'data' in res['data']['children'][-1]:
                    self.last_post_name = res['data']['children'][-1]['data']['name']
                for post in res['data']['children']:
                    post_data = self.Extract_Relevant_Data(post)
                    
                    if post_data and (post_data['title'] or post_data['body']):
                        test = extracted_data.append(post_data)
                        
                    print(test)
                    
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
            
            return extracted_data
        
        elif response.status_code == 401:
            print("Refreshing token...")
            Oauth_init = Oauth()
            self.Oauth_Token = Oauth_init.get_Oauth_token()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    
    def Extract_Relevant_Data(self, text):
        try:
            if 'data' in text:
                post_data = text['data']
            else:
                post_data = text
            
            extracted = {
                'title': post_data.get('title', ''),
                'body': post_data.get('selftext', ''),
                'subreddit': post_data.get('subreddit', ''),
                'post_id': post_data.get('id', ''),
                'created_utc': post_data.get('created_utc', '')
            }
            
            print(extracted)
            
            return extracted
        except Exception as e:
            return None
           
posts = RedditPosts()
posts.GetPosts()