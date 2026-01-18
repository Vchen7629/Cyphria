from typing import Callable
from psycopg_pool import ConnectionPool
from datetime import datetime, timezone
from unittest.mock import MagicMock
from src.worker import StartService

def test_worker_exits_immediately_when_no_comments(create_sentiment_service: StartService, mock_absa: MagicMock) -> None:
    """Worker should exit immediately when no unprocessed comments exist for category"""
    worker = create_sentiment_service

    worker.run()

    mock_absa.SentimentAnalysis.assert_not_called()


def test_worker_exits_after_processing_single_batch(db_pool: ConnectionPool, create_sentiment_service: StartService) -> None:
    """Worker should process all comments and exit when done"""
    # Insert test comments
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            for i in range(5):
                cursor.execute("""
                    INSERT INTO raw_comments (
                        comment_id, post_id, comment_body, detected_products, subreddit,
                        author, score, created_utc, category, sentiment_processed
                    ) VALUES (
                        %s, 'post_1', 'Great GPU performance', ARRAY['rtx 4090'], 'nvidia',
                        'user', 10, %s, 'GPU', FALSE
                    )
                """, (f'comment_{i}', datetime(2024, 1, 1, 12, i, 0, tzinfo=timezone.utc)))
        conn.commit()

    worker = create_sentiment_service
    worker.run()

    # Verify all comments are now marked as processed
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM raw_comments
                WHERE category = 'GPU' AND sentiment_processed = FALSE
            """)
            result = cursor.fetchone()
            unprocessed_count = result[0] if result else 0

            cursor.execute("""
                SELECT COUNT(*) FROM raw_comments
                WHERE category = 'GPU' AND sentiment_processed = TRUE
            """)
            result = cursor.fetchone()
            processed_count = result[0] if result else 0

    assert unprocessed_count == 0, "All comments should be marked as processed"
    assert processed_count == 5, "All 5 comments should be processed"


def test_worker_processes_multiple_batches_until_done(db_pool: ConnectionPool, create_sentiment_service: StartService) -> None:
    """Worker should process multiple batches and exit when all done"""
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            for i in range(10):
                cursor.execute("""
                    INSERT INTO raw_comments (
                        comment_id, post_id, comment_body, detected_products, subreddit,
                        author, score, created_utc, category, sentiment_processed
                    ) VALUES (
                        %s, 'post_1', 'Amazing GPU', ARRAY['rtx 4090'], 'nvidia',
                        'user', 10, %s, 'GPU', FALSE
                    )
                """, (f'batch_comment_{i}', datetime(2024, 1, 1, 12, i, 0, tzinfo=timezone.utc)))
        conn.commit()

    worker = create_sentiment_service
    worker.run()

    # Verify all comments processed
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM raw_comments
                WHERE category = 'GPU' AND sentiment_processed = FALSE
            """)
            result = cursor.fetchone()
            unprocessed_count = result[0] if result else 0

    assert unprocessed_count == 0, "All GPU comments should be processed"
