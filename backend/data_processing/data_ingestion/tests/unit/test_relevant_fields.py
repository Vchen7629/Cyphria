from types import SimpleNamespace
from worker.preprocessing.relevant_fields import process_post, RedditPost
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))


# Helper for mocking raw reddit post
def reddit_mock_data(**overrides):
    base = {
        "title": "Test Title",
        "selftext": "Test Body",
        "subreddit": SimpleNamespace(display_name="gaming"),
        "created_utc": 1696612345,
        "id": "abc123",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


# Normal Behavior (Expected)
def test_process_post_regular():
    data = reddit_mock_data()
    post = process_post(data)

    assert isinstance(post, RedditPost)  # type checking
    assert post.body == "Test Title Test Body"
    assert post.subreddit == "gaming"
    assert post.id == "abc123"


# edge case: empty title
def test_empty_title():
    data = reddit_mock_data(title="")
    post = process_post(data)

    assert post.body == "Test Body"


# edge case: empty selftext
def test_empty_selftext():
    data = reddit_mock_data(selftext="")
    post = process_post(data)

    assert post.body == "Test Title"


# edge case: empty selftext and title
def test_empty_selftext_title():
    data = reddit_mock_data(title="", selftext="")
    post = process_post(data)

    assert post.body == ""


# testing if unicode is picked up
def test_process_post_unicode():
    sub = reddit_mock_data(title="🚀🔥")
    post = process_post(sub)

    assert post.body == "🚀🔥 Test Body"
