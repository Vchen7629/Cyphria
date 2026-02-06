from datetime import datetime
from datetime import timezone
from unittest.mock import MagicMock
from src.api.schemas import ProcessedRedditComment
import pytest


@pytest.fixture
def mock_reddit_client() -> MagicMock:
    """Mock reddit client"""
    client = MagicMock()
    client.user.me.return_value = MagicMock(name="test_user")
    return client


@pytest.fixture
def mock_reddit_comment() -> ProcessedRedditComment:
    """Mocks one reddit comment"""
    return ProcessedRedditComment(
        comment_id="idk",
        post_id="test_post",
        comment_body="Test comment",
        detected_products=["RTX 4090"],
        subreddit="nvidia",
        author="test_user",
        score=10,
        timestamp=datetime.now(timezone.utc),
        topic="GPU",
    )
