from src.utils.category_to_subreddit_mapping import category_to_subreddit_mapping

def test_unknown_category() -> None:
    """Unknown category should return an empty list"""
    assert category_to_subreddit_mapping(None, "idk") == []

def test_known_category() -> None:
    """Known category should return a list of correct subreddits"""
    result = category_to_subreddit_mapping(None, "GPU")

    assert result == ["nvidia", "radeon", "amd", "IntelArc", "buildapc", "gamingpc", "pcbuild", "hardware"] 

def test_case_insensitivity() -> None:
    """Category should still match with not matching case"""
    result = category_to_subreddit_mapping(None, "gPu")

    assert result == ["nvidia", "radeon", "amd", "IntelArc", "buildapc", "gamingpc", "pcbuild", "hardware"]

def test_white_space() -> None:
    """Category name with white space should still match"""
    result = category_to_subreddit_mapping(None, " gpu ")

    assert result == ["nvidia", "radeon", "amd", "IntelArc", "buildapc", "gamingpc", "pcbuild", "hardware"]