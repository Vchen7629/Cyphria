import requests, praw
from preprocessing import language_filter, export_csv, remove_noise
from components import reddit_authentication

class RedditPosts:
    def __init__(self):
        self.filter_instance = remove_noise.removeNoise()
        self.reddit_instance = reddit_authentication.Auth().createRedditClient()
        self.old_reddit_content = remove_noise.removeNoise()

    def processData(self, apiRes):
        title = apiRes.title
        selftext = apiRes.selftext
        body = title + " " + selftext
        subreddit = apiRes.subreddit.display_name
        created_utc = apiRes.created_utc
        id = apiRes.id

        if language_filter.isEnglish(body) and self.old_reddit_content.removeOldRedditPosts(body):
            filter_url = self.filter_instance.removeURL(body)
            filter_stopwords = self.filter_instance.removeStopWords(filter_url)
            filter_brackets = self.filter_instance.removeBrackets(filter_stopwords)

            export_csv.exportCSV(filter_brackets, subreddit)

    def GetPosts(self):
        history = list(self.reddit_instance.subreddit("eatsandwiches").new(limit=50))
        history2 = list(self.reddit_instance.subreddit("cooking").new(limit=50))
        history3 = list(self.reddit_instance.subreddit("budgetFood").new(limit=50))
        
        for submission in history:
            self.processData(submission)
        
        for submission in history2:
            self.processData(submission)
        
        for submission in history3:
            self.processData(submission)
        
            
           
posts = RedditPosts()

if __name__ == "__main__":
    posts.GetPosts()
    print("Closing producer.")
