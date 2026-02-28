from typing import Any
from unittest.mock import patch
from unittest.mock import MagicMock
from src.api.schemas import ProcessedRedditComment
from src.ingestion_service import IngestionService
import pytest


def test_no_posts_returns_zero_counts(create_ingestion_service: IngestionService) -> None:
    """Worker should return 0 for all counts when there are 0 posts to process"""
    service = create_ingestion_service

    with patch.object(service, "_fetch_all_posts", return_value=[]):
        result = service.run_ingestion_pipeline()

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
        result = service.run_ingestion_pipeline()

    assert result.posts_processed == 1
    assert result.comments_processed == 0  # filtered comments are not counted as processed
    assert result.comments_inserted == 0  # all invalid comments should never be inserted into db


@pytest.mark.parametrize(
    argnames="comment_count,posts_processed,comments_processed,comments_inserted,batch_call_count,batch_sizes",
    argvalues=[
        (100, 1, 100, 100, 1, [100]),  # testing that exactly 100 comments triggers batch
        (99, 1, 99, 99, 1, [99]),  # testing that 99 also works
        (101, 1, 101, 101, 2, [100, 1]),  # testing that 101 comments creates 2 batches
    ],
)
def test_comments_triggers_batch(
    comment_count: int,
    posts_processed: int,
    comments_processed: int,
    comments_inserted: int,
    batch_call_count: int,
    batch_sizes: list[int],
    create_ingestion_service: IngestionService,
    mock_reddit_comment: ProcessedRedditComment,
) -> None:
    """Exactly 100 comments should trigger one batch insert at boundary"""
    service = create_ingestion_service

    mock_post = MagicMock(id="test_post")
    mock_comments = [MagicMock(id=f"c_{i}") for i in range(comment_count)]

    def mock_process_comment(_comment: Any, _detector: Any, _topic: Any) -> ProcessedRedditComment:
        return mock_reddit_comment.model_copy(update={"comment_id": f"rc_{_comment.id}"})

    batch_insert_calls: dict[str, Any] = {"count": 0, "sizes": []} # type: ignore

    def track_batch_insert(comment_list: list[ProcessedRedditComment]) -> None:
        batch_insert_calls["count"] += 1
        batch_insert_calls["sizes"].append(len(comment_list))

    with (
        patch.object(service, "_fetch_all_posts", return_value=[mock_post]),
        patch("src.ingestion_service.fetch_comments", return_value=mock_comments),
        patch.object(service, "_process_comment", side_effect=mock_process_comment),
        patch.object(service, "_batch_insert_to_db", side_effect=track_batch_insert),
    ):
        result = service.run_ingestion_pipeline()

    assert result.posts_processed == posts_processed
    assert result.comments_processed == comments_processed
    assert result.comments_inserted == comments_inserted
    assert batch_insert_calls["count"] == batch_call_count  # One batch at boundary
    assert batch_insert_calls["sizes"] == batch_sizes


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
        result = service.run_ingestion_pipeline()

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
        result = service.run_ingestion_pipeline()

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
        result = service.run_ingestion_pipeline()

    assert result.posts_processed == 2
    assert result.comments_processed == 0  # comment from post_2 was filtered out (returned None)
    assert result.comments_inserted == 0
