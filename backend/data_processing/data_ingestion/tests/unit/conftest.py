import pytest
from unittest.mock import Mock, PropertyMock

@pytest.fixture
def mock_logger():
    """Mock StructuredLogger Instance"""
    logger = Mock()
    logger.error = Mock()
    logger.info = Mock()

@pytest.fixture
def mock_submission():
    """Mock PRAW Submission object (reddit post)"""
    submission = Mock()
    submission.id = "xyz123"
    submission.title = "Test Post"
    submission.selftext = "Test post content"
    submission.created_utc = 1704067200.0
    submission.score = 100
    submission.num_comments = 5

    comment_forest = Mock()
    comment_forest.replace_more = Mock(return_value=[])
    comment_forest.list = Mock(return_value=[])

    type(submission).comments = PropertyMock(return_value=comment_forest)

    return submission