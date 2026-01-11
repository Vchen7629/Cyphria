import time
from prawcore.exceptions import Forbidden  # type: ignore
import praw  # type: ignore
from ..data_fetching.export_csv import ExportCSV
from ..data_fetching.reddit_authentication import Auth
from ...preprocessing.remove_stopwords import stop_words
from ...preprocessing.remove_url import remove_url


def extract_data(apiRes: praw.models.Submission) -> tuple[str, str]:
    title = apiRes.title
    selftext = apiRes.selftext
    body = title + " " + selftext
    subreddit = apiRes.subreddit.display_name
    # created_utc = apiRes.created_utc
    # id = apiRes.id

    return (
        body,
        subreddit,
    )


def get_posts() -> list[praw.models.Submission] | None:
    reddit_instance = Auth(
        "Reddit-Api-Client-ID",
        "Reddit-Api-Client-Secret",
        "Reddit-Account-Username",
        "Reddit-Account-Password",
    ).createRedditClient()
    try:
        history = list(reddit_instance.subreddit("mechanic").new(limit=150))

        return history
    except Forbidden as e:
        print(f"Error fetching: {e}")
        return None


if __name__ == "__main__":
    s_time = time.perf_counter()
    posts_arr: list[str] = []
    rawpost = get_posts()
    if rawpost is not None:
        for post in rawpost:
            body, subreddit = extract_data(post)
            no_url = remove_url(body)
            no_stopwords = stop_words(no_url)
            ExportCSV(no_stopwords, subreddit)
    else:
        print("No posts fetched")

    e_time = time.perf_counter()
    exec = e_time - s_time
    print(f"total took: {exec} seconds")
