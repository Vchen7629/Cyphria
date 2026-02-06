from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from src.core.reddit_client_instance import createRedditClient
import praw
from src.core.logger import StructuredLogger
import prawcore
from src.utils.fetch_post import fetch_post_delayed
from praw.reddit import Submission

def fetch_all_posts(reddit_client: praw.Reddit, logger: StructuredLogger,subreddit_list: list[str]) -> list[Submission]:
    """
    Fetch posts from all subreddits with per-subreddit error handling

    Returns:
        all_posts: list containing reddit post submission objects
    """
    all_posts = []
    max_praw_connections: int = 7 # praw supports 10 max but using 5 to avoid rate limits

    with ThreadPoolExecutor(max_workers=max_praw_connections) as executor:
        futures = {
            executor.submit(fetch_post_delayed, reddit_client, subreddit, logger): subreddit
            for subreddit in subreddit_list
        }
        for future in as_completed(futures):
            subreddit = futures[future] 
            try:
                posts = future.result()
                if posts:
                    all_posts.extend(posts)
            except prawcore.exceptions.ServerError as e:
                logger.error(
                    event_type="Subreddit Fetch",
                    message=f"Reddit API server error for r/{subreddit}: {e}",
                )
            except Exception as e:
                logger.error(
                    event_type="Subreddit Fetch", message=f"Failed to fetch from r/{subreddit}: {e}"
                )
                # python will automatically continue the loop if the exception as thrown
        
    return all_posts

if __name__ == "__main__":
    fetch_all_posts(
        createRedditClient(), 
        StructuredLogger(pod="idk"), 
 ["cameras", "photography", "Photography_Gear", "canon", "nikon", "SonyAlpha", "fujifilm", "fujifilmX", "Lumix", "Leica", "pentax", "olympuscamera", "DSLR"]    )