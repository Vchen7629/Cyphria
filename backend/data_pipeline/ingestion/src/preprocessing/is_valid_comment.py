from praw.models import Comment


def is_valid_comment(comment: Comment) -> bool:
    """
    Filter low-quality comments using multiple signals

    1. length of comment: so super short comments like
    2. Upvotes: filters out downvoted or ignored comments
    3. Bot detection: filters out comments from moderator or bots
    4. Deleted/Removed: filters out deleted/removed comments

    Args:
        comment: Reddit comment object

    Returns:
        Bool: True or False so only posts that pass the filters get sent downstream
            via kafka to be processed
    """
    if comment.body in ["[deleted]", "[removed]"]:
        return False

    if comment.author is None:
        return False

    if len(comment.body) < 20:
        return False

    # filters out downvoted/ignored comments
    if comment.score < 1:
        return False

    bot_indicators = ["bot", "moderator", "automod"]
    if any(indicator in comment.author.name.lower() for indicator in bot_indicators):
        return False

    return True
