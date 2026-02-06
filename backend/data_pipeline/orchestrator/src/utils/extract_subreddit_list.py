from src.config.mappings import TOPICSUBREDDIT
from src.config.mappings import CATEGORYTOPIC

def extract_subreddit_list(category: str) -> list[str]:
    """
    Build a set containing a list of all unique subreddits that need
    to be fetched from for the current product category

    Args:
        category: the category we are processing

    Returns:
        a list containing unique subreddit strings
    """
    topics = CATEGORYTOPIC.get(category.upper().strip(), [])

    subreddits = set()
    for topic in topics:
        topic_subreddits = TOPICSUBREDDIT.get(topic, [])
        subreddits.update(topic_subreddits)

    return list(subreddits)