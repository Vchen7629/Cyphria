from src.worker import IngestionService
from src.preprocessing.relevant_fields import RedditComment
from typing import Callable, Any
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

def test_cancel_flag_stops_worker_at_comment_level(create_ingestion_service: Callable[[], IngestionService]) -> None:
    """cancel_requested flag should stop worker loop at comment iteration level"""
    service = create_ingestion_service()

    mock_post = MagicMock(id="test_post")
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(20)]
    comments_processed = {"count": 0}

    def mock_process_comment(_comment: Any) -> RedditComment | None:
        comments_processed["count"] += 1
        if comments_processed["count"] >= 5:
            service.cancel_requested = True
        return create_reddit_comment(f"rc_{comments_processed['count']}")

    with patch.object(service, '_fetch_all_posts', return_value=[mock_post]), \
         patch('src.worker.fetch_comments', return_value=mock_comments), \
         patch.object(service, '_process_comment', side_effect=mock_process_comment):
        result = service.run()

    assert result.cancelled is True
    assert comments_processed["count"] < 20

def test_cancel_flag_stops_at_post_level(create_ingestion_service: Callable[[], IngestionService]) -> None:
    """cancel_requested flag should break out of post iteration loop"""
    service = create_ingestion_service()

    posts = [MagicMock(id=f"post_{i}") for i in range(5)]
    posts_processed = {"count": 0}

    def mock_fetch_comments(_post: Any, _logger: Any) -> list[MagicMock]:
        posts_processed["count"] += 1
        if posts_processed["count"] >= 2:
            service.cancel_requested = True
        return []

    with patch.object(service, '_fetch_all_posts', return_value=posts), \
         patch('src.worker.fetch_comments', side_effect=mock_fetch_comments):
        result = service.run()

    assert result.cancelled is True
    assert posts_processed["count"] == 2

def test_remaining_batch_saved_on_shutdown(db_pool: ConnectionPool, create_ingestion_service: Callable[[], IngestionService]) -> None:
    """Remaining comments in batch should be saved when shutdown occurs"""
    service = create_ingestion_service()

    mock_post = MagicMock(id="test_post")
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(50)]
    comments_processed = {"count": 0}

    def mock_process_comment(_comment: Any) -> RedditComment | None:
        comments_processed["count"] += 1
        if comments_processed["count"] >= 30:
            service.cancel_requested = True
        return create_reddit_comment(f"rc_{comments_processed['count']}")

    with patch.object(service, '_fetch_all_posts', return_value=[mock_post]), \
         patch('src.worker.fetch_comments', return_value=mock_comments), \
         patch.object(service, '_process_comment', side_effect=mock_process_comment):
        result = service.run()

    assert result.comments_inserted == 30

    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM raw_comments")
            count = cursor.fetchone()
            assert count is not None
            assert count[0] == 30

def test_shutdown_after_batch_insert_no_duplicate_save(db_pool: ConnectionPool, create_ingestion_service: Callable[[], IngestionService],) -> None:
    """When shutdown occurs right after a batch insert, no duplicate data should be saved"""
    service = create_ingestion_service()

    # 100 comments = exactly one batch
    mock_post = MagicMock(id="test_post")
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(100)]

    original_batch_insert = service._batch_insert_to_db

    def batch_insert_then_shutdown(comments: list[RedditComment]) -> None:
        original_batch_insert(comments)
        service.cancel_requested = True

    def mock_process_comment(comment: Any) -> RedditComment | None:
        return create_reddit_comment(comment.id)

    with patch.object(service, '_fetch_all_posts', return_value=[mock_post]), \
         patch('src.worker.fetch_comments', return_value=mock_comments), \
         patch.object(service, '_process_comment', side_effect=mock_process_comment), \
         patch.object(service, '_batch_insert_to_db', side_effect=batch_insert_then_shutdown):
        result = service.run()
    
    assert result.comments_inserted == 100

    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM raw_comments")
            count = cursor.fetchone()
            assert count is not None
            assert count[0] == 100