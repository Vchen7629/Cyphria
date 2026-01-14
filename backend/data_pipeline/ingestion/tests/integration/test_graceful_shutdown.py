from src.preprocessing.relevant_fields import RedditComment
import pytest
from typing import Callable, Any
from src.worker import Worker
from psycopg_pool.pool import ConnectionPool
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone


def create_reddit_comment(comment_id: str) -> RedditComment:
    """Helper to create RedditComment with unique ID"""
    return RedditComment(
        comment_id=comment_id,
        post_id="test_post",
        comment_body="Test comment",
        detected_products=["RTX 4090"],
        subreddit="nvidia",
        author="test_user",
        score=10,
        timestamp=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_post() -> MagicMock:
    """Create a mock Praw Submission Object"""
    post = MagicMock()
    post.id = 'test_post_1'
    return post


def test_shutdown_flag_stops_worker_at_comment_level(
    db_pool: ConnectionPool,
    create_worker: Callable[[], Worker],
    mock_post: MagicMock
) -> None:
    """Shutdown requested flag should stop worker loop at comment iteration level"""
    service = create_worker()

    mock_comments = [MagicMock(id=f"c_{i}") for i in range(20)]
    comments_processed = {"count": 0}

    def mock_process_comment(_comment: Any) -> RedditComment | None:
        comments_processed["count"] += 1
        if comments_processed["count"] >= 5:
            service.shutdown_requested = True
        return create_reddit_comment(f"rc_{comments_processed['count']}")

    with patch.object(service, '_fetch_all_posts', return_value=[mock_post]), \
         patch('src.worker.fetch_comments', return_value=mock_comments), \
         patch.object(service, '_process_comment', side_effect=mock_process_comment):
        service.run()

    assert service.shutdown_requested is True
    assert comments_processed["count"] < 20

def test_cleanup_called_on_exception(create_worker: Callable[[], Worker], mock_post: MagicMock) -> None:
    """Cleanup should be called when an exception occurs"""
    service = create_worker()

    with patch.object(service, '_fetch_all_posts', return_value=[mock_post]), \
         patch('src.worker.fetch_comments', side_effect=RuntimeError("Test error")), \
         patch.object(service, '_cleanup') as mock_cleanup:
        with pytest.raises(RuntimeError):
            service.run()
        mock_cleanup.assert_called_once()

def test_cleanup_called_on_shutdown(db_pool: ConnectionPool) -> None:
    """Cleanup method should be called when worker shuts down"""
    with patch.object(Worker, '_database_conn_lifespan'), \
         patch('src.worker.createRedditClient'), \
         patch('src.worker.category_to_subreddit_mapping', return_value=['test_subreddit']), \
         patch('src.worker.DetectorFactory.get_detector'):
        service = Worker()
        service.db_pool = db_pool

        service.shutdown_requested = True

        # Mock cleanup without wrapping to prevent pool closure
        with patch.object(service, '_cleanup') as mock_cleanup:
            service.run()

            mock_cleanup.assert_called_once()

def test_remaining_batch_saved_on_shutdown(db_pool: ConnectionPool, create_worker: Callable[[], Worker], mock_post: MagicMock) -> None:
    """Remaining comments in batch should be saved when shutdown occurs"""
    service = create_worker()

    mock_comments = [MagicMock(id=f"c_{i}") for i in range(50)]
    comments_processed = {"count": 0}

    def mock_process_comment(_comment: Any) -> RedditComment | None:
        comments_processed["count"] += 1
        if comments_processed["count"] >= 30:
            service.shutdown_requested = True
        return create_reddit_comment(f"rc_{comments_processed['count']}")

    with patch.object(service, '_fetch_all_posts', return_value=[mock_post]), \
         patch('src.worker.fetch_comments', return_value=mock_comments), \
         patch.object(service, '_process_comment', side_effect=mock_process_comment):
        service.run()

    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM raw_comments")
            count = cursor.fetchone()
            assert count is not None
            assert count[0] == 30


def test_shutdown_stops_at_post_level(
    db_pool: ConnectionPool,
    create_worker: Callable[[], Worker]
) -> None:
    """Shutdown_requested flag should break out of post iteration loop"""
    service = create_worker()

    posts = [MagicMock(id=f"post_{i}") for i in range(5)]
    posts_processed = {"count": 0}

    def mock_fetch_comments(_post: Any, _logger: Any) -> list[MagicMock]:
        posts_processed["count"] += 1
        if posts_processed["count"] >= 2:
            service.shutdown_requested = True
        return []

    with patch.object(service, '_fetch_all_posts', return_value=posts), \
         patch('src.worker.fetch_comments', side_effect=mock_fetch_comments):
        service.run()

    assert service.shutdown_requested is True
    assert posts_processed["count"] == 2


def test_shutdown_after_batch_insert_no_duplicate_save(
    db_pool: ConnectionPool,
    create_worker: Callable[[], Worker],
    mock_post: MagicMock
) -> None:
    """When shutdown occurs right after a batch insert, no duplicate data should be saved"""
    service = create_worker()

    # 100 comments = exactly one batch
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(100)]

    original_batch_insert = service._batch_insert_to_db

    def batch_insert_then_shutdown(comments: list[RedditComment]) -> None:
        original_batch_insert(comments)
        service.shutdown_requested = True

    def mock_process_comment(comment: Any) -> RedditComment | None:
        return create_reddit_comment(comment.id)

    with patch.object(service, '_fetch_all_posts', return_value=[mock_post]), \
         patch('src.worker.fetch_comments', return_value=mock_comments), \
         patch.object(service, '_process_comment', side_effect=mock_process_comment), \
         patch.object(service, '_batch_insert_to_db', side_effect=batch_insert_then_shutdown):
        service.run()

    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM raw_comments")
            count = cursor.fetchone()
            assert count is not None
            assert count[0] == 100
        