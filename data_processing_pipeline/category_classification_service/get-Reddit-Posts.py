import time, multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from prawcore.exceptions import Forbidden
from preprocessing import language_filter, export_csv, remove_noise, lexicon_substitution
from components import reddit_authentication

def batch(batch):
    batch_arr = []
    for post in batch:
        checkvalid = posts.checkValid(post)
        if checkvalid:
            text = posts.removeNoise(post)
            cleaned = posts.substituteLexicon(text)
            batch_arr.append(cleaned)
    return batch_arr

class RedditPosts:
    def __init__(self):
        self.reddit_instance = reddit_authentication.Auth().createRedditClient()
        self.lexicon_instance = lexicon_substitution.SubTextInRedditPosts()
        self.filter_instance = remove_noise.removeNoise()
        self.invalid_instance = remove_noise.removeNoise()

    def substituteLexicon(self,rawtext):
        s5_time = time.perf_counter()
        sub_age = self.lexicon_instance.replaceAge(rawtext)
        e5_time = time.perf_counter()
        s6_time = time.perf_counter()
        sub_money = self.lexicon_instance.replaceNumericalMoney(sub_age)
        e6_time = time.perf_counter()
        s7_time = time.perf_counter()
        sub_stock_name = self.lexicon_instance.replaceStockName(sub_money)
        e7_time = time.perf_counter()
        s8_time = time.perf_counter()
        sub_programming_name = self.lexicon_instance.replaceProgrammingLanguage(sub_stock_name)
        e8_time = time.perf_counter()
        s9_time = time.perf_counter()
        sub_gpu_name = self.lexicon_instance.replaceProgrammingLanguage(sub_programming_name)
        e9_time = time.perf_counter()
        s10_time = time.perf_counter()
        sub_vehicle_name = self.lexicon_instance.replaceVehicleBrands(sub_gpu_name)
        e10_time = time.perf_counter()

        exec5 = e5_time - s5_time
        print(f"sub age took: {exec5} seconds")
        exec6 = e6_time - s6_time
        print(f"sub money took: {exec6} seconds")
        exec7 = e7_time - s7_time
        print(f"sub stock took: {exec7} seconds")
        exec8 = e8_time - s8_time
        print(f"sub programming name took: {exec8} seconds")
        exec9 = e9_time - s9_time
        print(f"sub gpu name took: {exec9} seconds")
        exec10 = e10_time - s10_time
        print(f"sub vehicle brand took: {exec10} seconds")

        return sub_vehicle_name

    def extractData(self, apiRes):
        title = apiRes.title
        selftext = apiRes.selftext
        print("huh", selftext)
        body = title + " " + selftext
        subreddit = apiRes.subreddit.display_name
        created_utc = apiRes.created_utc
        id = apiRes.id
            
        return body

    def checkValid(self, text):
        if language_filter.isEnglish(text) and self.invalid_instance.removeOldRedditPosts(text):
            return True
        else:
            return False

    def removeNoise(self, rawtext):
            s1_time = time.perf_counter()
            filter_url = self.filter_instance.removeURL(rawtext)
            e1_time = time.perf_counter()
            s2_time = time.perf_counter()
            filter_stopwords = self.filter_instance.removeStopWords(filter_url)
            e2_time = time.perf_counter()
            s3_time = time.perf_counter()
            filter_commas = self.filter_instance.removeCommas(filter_stopwords)
            e3_time = time.perf_counter()
            s4_time = time.perf_counter()
            filter_brackets = self.filter_instance.removeBrackets(filter_commas)
            e4_time = time.perf_counter()

            exec1 = e1_time - s1_time
            print(f"filterURL took: {exec1} seconds")
            exec2 = e2_time - s2_time
            print(f"filterstopwords took: {exec2} seconds")
            exec3 = e3_time - s3_time
            print(f"filtercommas took: {exec3} seconds")
            exec4 = e4_time - s4_time
            print(f"filterbrackets took: {exec4} seconds")

            return filter_brackets



    def GetPosts(self):
        try:
            history = list(self.reddit_instance.subreddit("politicaldiscussion").new(limit=10))
            #history2 = list(self.reddit_instance.subreddit("socialism").new(limit=150))
            #history3 = list(self.reddit_instance.subreddit("neutralpolitics").new(limit=150))
            #history4 = list(self.reddit_instance.subreddit("politicaldiscussion").new(limit=200))
            #history5 = list(self.reddit_instance.subreddit("basketballcards").new(limit=20))
            
            
                #self.extractData(submission)
            return history

            #for submission in history5:
            #    self.processData(submission)
        except Forbidden as e:
            print(f"Error fetching", e)
            
           
posts = RedditPosts()

if __name__ == "__main__":
    s_time = time.perf_counter()
    posts_arr = []
    rawpost = posts.GetPosts()
    for post in rawpost:
        body = posts.extractData(post)
        posts_arr.append(body)

    batches = [posts_arr[i:i+50] for i in range(0, len(posts_arr), 50)]

    with ThreadPool(processes=16) as pool:
        cleaned_text = pool.map(batch, batches)
    
    
    for text in cleaned_text:
        export_csv.exportCSV(text)
    #if language_filter.isEnglish(body) and self.old_reddit_content.removeOldRedditPosts(body):
    #        text = self.removeNoise(body)
    e_time = time.perf_counter()
    exec = e_time - s_time
    print(f"total took: {exec} seconds")
    print("Closing producer.")
