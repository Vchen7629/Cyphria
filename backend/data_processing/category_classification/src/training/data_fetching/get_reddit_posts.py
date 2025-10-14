import time
from prawcore.exceptions import Forbidden

from ..data_fetching.export_csv import export_csv
from ..data_fetching.reddit_authentication import reddit_authentication
from ...preprocessing.remove_stopwords import stop_words
from ...preprocessing.remove_url import remove_url

def extract_data(
    apiRes,
) -> tuple[
    str,
    str,
]:
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


def get_posts() -> list[
    tuple[
        str,
        str,
        str,
    ]
]:
    reddit_instance = reddit_authentication.Auth(
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


def get_posts2() -> list[
    tuple[
        str,
        str,
        str,
    ]
]:
    reddit_instance = reddit_authentication.Auth(
        "Reddit-Api-Client-ID",
        "Reddit-Api-Client-Secret",
        "Reddit-Account-Username",
        "Reddit-Account-Password",
    ).createRedditClient()
    try:
        history = list(reddit_instance.subreddit("candy").new(limit=300))

        return history
    except Forbidden as e:
        print(f"Error fetching: {e}")


def get_posts3() -> list[
    tuple[
        str,
        str,
        str,
    ]
]:
    reddit_instance = reddit_authentication.Auth(
        "Reddit-Api-Client-ID",
        "Reddit-Api-Client-Secret",
        "Reddit-Account-Username",
        "Reddit-Account-Password",
    ).createRedditClient()
    try:
        history = list(reddit_instance.subreddit("CarHelp").new(limit=20))

        return history
    except Forbidden as e:
        print(f"Error fetching: {e}")


if __name__ == "__main__":
    s_time = time.perf_counter()
    posts_arr: list[str] = []
    rawpost = get_posts()
    for post in rawpost:
        (
            body,
            subreddit,
        ) = extract_data(post)
        no_url = remove_url(body)
        no_stopwords = stop_words(no_url)
        export_csv.ExportCSV(
            no_stopwords,
            subreddit,
        )

    e_time = time.perf_counter()
    exec = e_time - s_time
    print(f"total took: {exec} seconds")
