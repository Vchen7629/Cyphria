from typing import Any
from unittest.mock import patch
from unittest.mock import MagicMock
from psycopg_pool import ConnectionPool
from src.ingestion_service import IngestionService
from src.preprocessing.relevant_fields import ProcessedRedditComment


def test_remaining_batch_saved_on_shutdown(
    db_pool: ConnectionPool,
    create_ingestion_service: IngestionService,
    mock_reddit_comment: ProcessedRedditComment,
) -> None:
    """Remaining comments in batch should be saved when shutdown occurs"""
    service = create_ingestion_service

    mock_post = MagicMock(id="test_post")
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(50)]
    comments_processed = {"count": 0}

    def mock_process_comment(
        _comment: Any, _detector: Any, _topic: Any
    ) -> ProcessedRedditComment | None:
        comments_processed["count"] += 1
        if comments_processed["count"] >= 30:
            service.cancel_requested = True
        reddit_comment = mock_reddit_comment.model_copy(
            update={"comment_id": f"rc_{comments_processed['count']}"}
        )
        return reddit_comment

    with (
        patch.object(service, "_fetch_all_posts", return_value=[mock_post]),
        patch("src.ingestion_service.fetch_comments", return_value=mock_comments),
        patch.object(service, "_process_comment", side_effect=mock_process_comment),
    ):
        result = service._run_ingestion_pipeline()

    assert result.comments_inserted == 30

    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM raw_comments")
            count = cursor.fetchone()
            assert count is not None
            assert count[0] == 30


def test_shutdown_after_batch_insert_no_duplicate_save(
    db_pool: ConnectionPool,
    create_ingestion_service: IngestionService,
    mock_reddit_comment: ProcessedRedditComment,
) -> None:
    """When shutdown occurs right after a batch insert, no duplicate data should be saved"""
    service = create_ingestion_service

    # 100 comments = exactly one batch
    mock_post = MagicMock(id="test_post")
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(100)]

    original_batch_insert = service._batch_insert_to_db

    def batch_insert_then_shutdown(comments: list[ProcessedRedditComment]) -> None:
        original_batch_insert(comments)
        service.cancel_requested = True

    def mock_process_comment(
        comment: Any, _detector: Any, _topic: Any
    ) -> ProcessedRedditComment | None:
        reddit_comment = mock_reddit_comment.model_copy(update={"comment_id": comment.id})
        return reddit_comment

    with (
        patch.object(service, "_fetch_all_posts", return_value=[mock_post]),
        patch("src.ingestion_service.fetch_comments", return_value=mock_comments),
        patch.object(service, "_process_comment", side_effect=mock_process_comment),
        patch.object(service, "_batch_insert_to_db", side_effect=batch_insert_then_shutdown),
    ):
        result = service._run_ingestion_pipeline()

    assert result.comments_inserted == 100

    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM raw_comments")
            count = cursor.fetchone()
            assert count is not None
            assert count[0] == 100
