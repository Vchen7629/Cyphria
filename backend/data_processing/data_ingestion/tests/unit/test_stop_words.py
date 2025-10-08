from worker.preprocessing.stop_words import stop_words
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))


def test_post_regular():
    text = "That cat had too much to drink"
    result = stop_words(text)

    assert result == "cat much drink"


def test_no_stopwords():
    text = "dog love popsicle"
    result = stop_words(text)

    assert result == "dog love popsicle"


def test_emojis():
    text = "🚀🔥 new python release!!!"
    result = stop_words(text)

    assert result == "🚀🔥 new python release!!!"
