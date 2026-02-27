from typing import Any
from unittest.mock import patch
from unittest.mock import MagicMock
from src.api.schemas import ProcessedRedditComment
from src.ingestion_service import IngestionService


def test_no_posts_returns_zero_counts(create_ingestion_service: IngestionService) -> None:
    """Worker should return 0 for all counts when there are 0 posts to process"""
    service = create_ingestion_service

    with patch.object(service, "_fetch_all_posts", return_value=[]):
        result = service._run_ingestion_pipeline()

    assert result.posts_processed == 0
    assert result.comments_processed == 0
    assert result.comments_inserted == 0

def test_all_comments_filtered_out(create_ingestion_service: IngestionService) -> None:
    """All comments filtered should result in 0 inserts and 0 processed"""
    service = create_ingestion_service

    mock_post = MagicMock(id="test_post")
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(10)]

    with (
        patch.object(service, "_fetch_all_posts", return_value=[mock_post]),
        patch("src.ingestion_service.fetch_comments", return_value=mock_comments),
        patch.object(service, "_process_comment", return_value=None),
    ):  # Mock this to none so it simulate failing being valid and filtered out
        result = service._run_ingestion_pipeline()

    assert result.posts_processed == 1
    assert result.comments_processed == 0  # filtered comments are not counted as processed
    assert result.comments_inserted == 0  # all invalid comments should never be inserted into db


def test_exactly_100_comments_triggers_batch(
    create_ingestion_service: IngestionService, mock_reddit_comment: ProcessedRedditComment
) -> None:
    """Exactly 100 comments should trigger one batch insert at boundary"""
    service = create_ingestion_service

    mock_post = MagicMock(id="test_post")
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(100)]

    def mock_process_comment(_comment: Any, _detector: Any, _topic: Any) -> ProcessedRedditComment:
        return mock_reddit_comment.model_copy(update={"comment_id": f"rc_{_comment.id}"})

    batch_insert_calls = {"count": 0}

    def track_batch_insert(_comment_list: list[ProcessedRedditComment]) -> None:
        batch_insert_calls["count"] += 1
        # Don't actually insert to DB in this test

    with (
        patch.object(service, "_fetch_all_posts", return_value=[mock_post]),
        patch("src.ingestion_service.fetch_comments", return_value=mock_comments),
        patch.object(service, "_process_comment", side_effect=mock_process_comment),
        patch.object(service, "_batch_insert_to_db", side_effect=track_batch_insert),
    ):
        result = service._run_ingestion_pipeline()

    assert result.posts_processed == 1
    assert result.comments_processed == 100
    assert result.comments_inserted == 100
    assert batch_insert_calls["count"] == 1  # One batch at boundary


def test_99_comments_only_final_batch(
    create_ingestion_service: IngestionService, mock_reddit_comment: ProcessedRedditComment
) -> None:
    """99 comments should only trigger final batch insert"""
    service = create_ingestion_service

    mock_post = MagicMock(id="test_post")
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(99)]

    def mock_process_comment(_comment: Any, _detector: Any, _topic: Any) -> ProcessedRedditComment:
        return mock_reddit_comment.model_copy(update={"comment_id": f"rc_{_comment.id}"})

    batch_insert_calls = {"count": 0}

    def track_batch_insert(comment_list: list[ProcessedRedditComment]) -> None:
        batch_insert_calls["count"] += 1
        assert len(comment_list) == 99  # Should be final batch with all 99

    with (
        patch.object(service, "_fetch_all_posts", return_value=[mock_post]),
        patch("src.ingestion_service.fetch_comments", return_value=mock_comments),
        patch.object(service, "_process_comment", side_effect=mock_process_comment),
        patch.object(service, "_batch_insert_to_db", side_effect=track_batch_insert),
    ):
        result = service._run_ingestion_pipeline()

    assert result.posts_processed == 1
    assert result.comments_processed == 99
    assert result.comments_inserted == 99
    assert batch_insert_calls["count"] == 1  # Only final batch


def test_101_comments_batch_plus_final(
    create_ingestion_service: IngestionService, mock_reddit_comment: ProcessedRedditComment
) -> None:
    """101 comments should trigger one batch insert + final batch"""
    service = create_ingestion_service

    mock_post = MagicMock(id="test_post")
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(101)]

    def mock_process_comment(_comment: Any, _detector: Any, _topic: Any) -> ProcessedRedditComment:
        return mock_reddit_comment.model_copy(update={"comment_id": f"rc_{_comment.id}"})

    batch_insert_calls: dict[str, Any] = {"count": 0, "sizes": []}  # type: ignore

    def track_batch_insert(comment_list: list[ProcessedRedditComment]) -> None:
        batch_insert_calls["count"] += 1
        batch_insert_calls["sizes"].append(len(comment_list))

    with (
        patch.object(service, "_fetch_all_posts", return_value=[mock_post]),
        patch("src.ingestion_service.fetch_comments", return_value=mock_comments),
        patch.object(service, "_process_comment", side_effect=mock_process_comment),
        patch.object(service, "_batch_insert_to_db", side_effect=track_batch_insert),
    ):
        result = service._run_ingestion_pipeline()

    assert result.posts_processed == 1
    assert result.comments_processed == 101
    assert result.comments_inserted == 101
    assert batch_insert_calls["count"] == 2  # One batch + final
    assert batch_insert_calls["sizes"] == [100, 1]  # First batch 100, final batch 1


def test_mixed_valid_invalid_comments(
    create_ingestion_service: IngestionService, mock_reddit_comment: ProcessedRedditComment
) -> None:
    """Mix of valid and invalid comments should only insert valid ones"""
    service = create_ingestion_service

    mock_post = MagicMock(id="test_post")
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(10)]

    def mock_process_comment(
        comment: Any, _detector: Any, _topic: Any
    ) -> ProcessedRedditComment | None:
        comment_num = int(comment.id.split("_")[1])
        # Only even numbered comments are valid
        if comment_num % 2 == 0:
            return mock_reddit_comment.model_copy(update={"comment_id": comment.id})
        return None

    with (
        patch.object(service, "_fetch_all_posts", return_value=[mock_post]),
        patch("src.ingestion_service.fetch_comments", return_value=mock_comments),
        patch.object(service, "_process_comment", side_effect=mock_process_comment),
        patch.object(service, "_batch_insert_to_db"),
    ):
        result = service._run_ingestion_pipeline()

    assert result.posts_processed == 1
    assert (
        result.comments_processed == 5
    )  # Only even numbered comments (0, 2, 4, 6, 8) are counted as processed
    assert result.comments_inserted == 5  # Only even numbered (0, 2, 4, 6, 8)


def test_multiple_posts_with_varying_comments(
    create_ingestion_service: IngestionService, mock_reddit_comment: ProcessedRedditComment
) -> None:
    """Multiple posts with different comment counts should track correctly"""
    service = create_ingestion_service

    mock_posts = [MagicMock(id="post_1"), MagicMock(id="post_2"), MagicMock(id="post_3")]

    def mock_fetch_comments(post: Any, _logger: Any) -> list[MagicMock]:
        if post.id == "post_1":
            return [MagicMock(id=f"c1_{i}") for i in range(5)]
        elif post.id == "post_2":
            return [MagicMock(id=f"c2_{i}") for i in range(10)]
        else:  # post_3
            return [MagicMock(id=f"c3_{i}") for i in range(3)]

    def mock_process_comment(_comment: Any, _detector: Any, _topic: Any) -> ProcessedRedditComment:
        return mock_reddit_comment.model_copy(update={"comment_id": _comment.id})

    with (
        patch.object(service, "_fetch_all_posts", return_value=mock_posts),
        patch("src.ingestion_service.fetch_comments", side_effect=mock_fetch_comments),
        patch.object(service, "_process_comment", side_effect=mock_process_comment),
        patch.object(service, "_batch_insert_to_db"),
    ):
        result = service._run_ingestion_pipeline()

    assert result.posts_processed == 3
    assert result.comments_processed == 18  # 5 + 10 + 3
    assert result.comments_inserted == 18


def test_post_with_no_comments(create_ingestion_service: IngestionService) -> None:
    """Post with no comments should still increment post counter"""
    service = create_ingestion_service

    mock_posts = [MagicMock(id="post_1"), MagicMock(id="post_2")]

    def mock_fetch_comments(post: Any, _logger: Any) -> list[MagicMock]:
        if post.id == "post_1":
            return []  # No comments
        else:
            return [MagicMock(id="c1")]

    with (
        patch.object(service, "_fetch_all_posts", return_value=mock_posts),
        patch("src.ingestion_service.fetch_comments", side_effect=mock_fetch_comments),
        patch.object(service, "_process_comment", return_value=None),
        patch.object(service, "_batch_insert_to_db"),
    ):
        result = service._run_ingestion_pipeline()

    assert result.posts_processed == 2
    assert result.comments_processed == 0  # comment from post_2 was filtered out (returned None)
    assert result.comments_inserted == 0
