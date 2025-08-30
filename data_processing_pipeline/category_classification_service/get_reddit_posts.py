import time
from multiprocessing.dummy import Pool as ThreadPool
from prawcore.exceptions import Forbidden
from preprocessing import export_csv
from components import reddit_authentication, process_data

def batch(batch):
    #process_instance = process_data.RedditPosts()
    #batch_arr = []

    #for post in batch:
    #    checkvalid = process_instance.checkValid(post)
    #    if checkvalid:
    #        text = process_instance.removeNoise(post)
    #        cleaned = process_instance.substituteLexicon(text)
    #        batch_arr.append(cleaned)
#
    #return batch_arr
    pass

def extractData(apiRes) -> tuple[str, str]:
    title = apiRes.title
    selftext = apiRes.selftext
    body = title + " " + selftext
    subreddit = apiRes.subreddit.display_name
    created_utc = apiRes.created_utc
    id = apiRes.id
            
    return body, subreddit

def GetPosts() -> list[tuple[str, str, str]]:
    reddit_instance = reddit_authentication.Auth(
        "Reddit-Api-Client-ID",
        "Reddit-Api-Client-Secret",
        "Reddit-Account-Username",
        "Reddit-Account-Password"
    ).createRedditClient()
    try:
        history = list(reddit_instance.subreddit("Toyota").new(limit=300))
        
        return history
            #for submission in history5:
            #    self.processData(submission)
    except Forbidden as e:
        print(f"Error fetching", e)
    
    #return history

def GetPosts2() -> list[tuple[str, str, str]]:
    reddit_instance = reddit_authentication.Auth(
        "Reddit-Api-Client-ID",
        "Reddit-Api-Client-Secret",
        "Reddit-Account-Username",
        "Reddit-Account-Password"
    ).createRedditClient()
    try:
        history = list(reddit_instance.subreddit("History").new(limit=300))
        
        return history
            #for submission in history5:
            #    self.processData(submission)
    except Forbidden as e:
        print(f"Error fetching", e)

def GetPosts3() -> list[tuple[str, str, str]]:
    reddit_instance = reddit_authentication.Auth(
        "Reddit-Api-Client-ID",
        "Reddit-Api-Client-Secret",
        "Reddit-Account-Username",
        "Reddit-Account-Password"
    ).createRedditClient()
    try:
        history = list(reddit_instance.subreddit("CarHelp").new(limit=200))
        
        return history
            #for submission in history5:
            #    self.processData(submission)
    except Forbidden as e:
        print(f"Error fetching", e)
            
           
if __name__ == "__main__":
    s_time = time.perf_counter()
    posts_arr: list[str] = []
    rawpost = GetPosts()
    for post in rawpost:
        body, subreddit = extractData(post)
        filter = process_data.RedditPosts().removeNoise(body)
        export_csv.exportCSV(filter, subreddit)
    #    posts_arr.append(body)

    #batches = [posts_arr[i:i+50] for i in range(0, len(posts_arr), 50)]
#
    #with ThreadPool(processes=16) as pool:
     #   cleaned_text = pool.map(batch, batches)
    
    #for text in cleaned_text:
    #    export_csv.exportCSV(text)

    e_time = time.perf_counter()
    exec = e_time - s_time
    print(f"total took: {exec} seconds")
