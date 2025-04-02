from oauth import Oauth
from langdetect import detect
import requests, requests.auth
from kafka_components.reddit_api_producer import r_producer

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
            english_only = []
            
            if 'data' in res and 'children' in res['data']:
                if res['data']['children'] and 'data' in res['data']['children'][-1]:
                    self.last_post_name = res['data']['children'][-1]['data']['name']
                for post in res['data']['children']:
                    post_data = self.Extract_Relevant_Data(post)
                    
                    if post_data and (post_data['body']):
                        if self.isEnglish(post_data):
                            english_only.append(post_data)
                            subreddit = post_data['subreddit']
                            print("hiiiiiiiiiiiiii", subreddit)
            
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
            
            r_producer.Send_Message(subreddit, english_only)
            
            print("english only: ", english_only)

            return english_only
        
        elif response.status_code == 401:
            print("Refreshing token...")
            Oauth_init = Oauth()
            self.Oauth_Token = Oauth_init.get_Oauth_token()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    
    def isEnglish(self, text):
        try:
            combined_text = text.get('body', '')
            return detect(combined_text) == 'en'
        except:
            return False
    
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
            
            #print(extracted)
            
            return extracted
        except Exception as e:
            return None
           
posts = RedditPosts()

if __name__ == "__main__":
    for i in range(5):
        posts.GetPosts()
    print("Closing producer.")
    r_producer.producer.close()