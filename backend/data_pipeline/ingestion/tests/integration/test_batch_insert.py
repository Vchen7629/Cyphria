from datetime import datetime, timezone
from testcontainers.postgres import PostgresContainer
from src.ingestion_service import IngestionService
from src.preprocessing.relevant_fields import ProcessedRedditComment
from src.db_utils.queries import batch_insert_raw_comments
import psycopg
import pytest


def test_worker_batch_insert_error_handling(worker_with_test_db: IngestionService) -> None:
    """Test that Worker properly propagates database errors during batch insert."""
    invalid_data = [
        {
            "comment_id": "invalid_test",
            "post_id": "post_1",
            "comment_body": None,  # type: ignore
            "detected_products": ["rtx 4090"],
            "subreddit": "nvidia",
            "author": "user1",
            "score": 10,
            "created_utc": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            "product_topic": worker_with_test_db._topic_list[0],
        }
    ]

    # This should raise a NotNullViolation error from the database
    with pytest.raises(psycopg.errors.NotNullViolation):
        with worker_with_test_db.db_pool.connection() as conn:
            batch_insert_raw_comments(conn, invalid_data)


def test_worker_batch_insert_with_connection_pool_multiple_batches(
    worker_with_test_db: IngestionService, postgres_container: PostgresContainer
) -> None:
    """
    Test that Worker can handle multiple sequential batch inserts using the connection pool.
    This simulates the actual worker flow where batches are inserted as they fill up.
    """
    # First batch
    batch1 = [
        ProcessedRedditComment(
            comment_id=f"batch1_{i}",
            post_id=f"post_{i}",
            comment_body=f"Batch 1 comment {i}",
            detected_products=["rtx 4090"],
            subreddit="nvidia",
            author=f"user_{i}",
            score=i,
            timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            topic="gpu",
        )
        for i in range(5)
    ]

    # Second batch
    batch2 = [
        ProcessedRedditComment(
            comment_id=f"batch2_{i}",
            post_id=f"post_{i}",
            comment_body=f"Batch 2 comment {i}",
            detected_products=["rtx 4080"],
            subreddit="nvidia",
            author=f"user_{i}",
            score=i,
            timestamp=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
            topic="gpu",
        )
        for i in range(5)
    ]

    # Insert both batches sequentially
    worker_with_test_db._batch_insert_to_db(batch1)
    worker_with_test_db._batch_insert_to_db(batch2)

    # Verify all comments from both batches were inserted
    # Convert SQLAlchemy URL to PostgreSQL URI for psycopg
    connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
    with psycopg.connect(connection_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM raw_comments;")
            result = cursor.fetchone()
            assert result is not None
            count = result[0]
            assert count == 10

            # Verify batch1 comments
            cursor.execute("SELECT COUNT(*) FROM raw_comments WHERE comment_id LIKE 'batch1_%';")
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 5

            # Verify batch2 comments
            cursor.execute("SELECT COUNT(*) FROM raw_comments WHERE comment_id LIKE 'batch2_%';")
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 5
