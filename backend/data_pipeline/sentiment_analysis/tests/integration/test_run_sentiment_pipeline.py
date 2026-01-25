from typing import Any
from unittest.mock import patch
from psycopg_pool import ConnectionPool
from src.sentiment_service import SentimentService
import time
import threading

def test_cancel_flag_mid_batch(db_pool: ConnectionPool, create_sentiment_service: SentimentService) -> None:
    """Shutdown_requested flag should cause worker loop to exit properly"""
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            for i in range(100):
                cursor.execute("""
                    INSERT INTO raw_comments (
                        comment_id, post_id, comment_body, detected_products, subreddit,
                        author, score, created_utc, product_topic, sentiment_processed
                    ) VALUES (
                        %s, 'p1', 'Test comment', ARRAY['product1'],
                        'test_sub', 'test_author', 10, NOW(), 'GPU', FALSE
                    )
                """, (f"c{i}",))

    service = create_sentiment_service

    # Use seperate thread to trigger cancel to prevent blocking
    def trigger_shutdown() -> None:
        time.sleep(0.5) # short delay so worker can process at least one batch
        service.cancel_requested = True

    shutdown_thread = threading.Thread(target=trigger_shutdown, daemon=True)
    shutdown_thread.start()

    service._run_sentiment_pipeline()

    assert service.cancel_requested is True

    # verify that some comments were processed before shutdown
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM raw_comments WHERE sentiment_processed = TRUE")

            count = cursor.fetchone()
            assert count is not None
            assert count[0] > 0

def test_no_data_loss_when_cancelled_between_batches(db_pool: ConnectionPool, create_sentiment_service: SentimentService) -> None:
    """Cancelling between batches shouln't cause data loss. All processed comments should be properly marked"""
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            for i in range(250):
                cursor.execute("""
                    INSERT INTO raw_comments (
                        comment_id, post_id, comment_body, detected_products, subreddit,
                        author, score, created_utc, product_topic, sentiment_processed
                    ) VALUES (
                        %s, 'p1', 'Test comment', ARRAY['product1'],
                        'test_sub', 'test_author', 10, NOW(), 'GPU', FALSE
                    )
                """, (f"c{i}",))

    service = create_sentiment_service

    # Track how many batches have been processed
    original_process_comments = service._process_comments
    batch_count = {"count": 0}

    def track_batches(comments: list[Any]) -> tuple[int, int]:
        result = original_process_comments(comments)
        batch_count["count"] += 1

        if batch_count["count"] == 1:
            service.cancel_requested = True
        return result

    with patch.object(service, '_process_comments', side_effect=track_batches):
        service._run_sentiment_pipeline()

    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            # Verify some comments were processed
            cursor.execute("SELECT COUNT(*) FROM raw_comments WHERE sentiment_processed = TRUE")
            processed_count = cursor.fetchone()
            assert processed_count is not None
            assert processed_count[0] > 0

            # Verify remaining comments are still unprocessed
            cursor.execute("SELECT COUNT(*) FROM raw_comments WHERE sentiment_processed = FALSE")
            unprocessed_count = cursor.fetchone()
            assert unprocessed_count is not None
            assert unprocessed_count[0] > 0

            assert processed_count[0] + unprocessed_count[0] == 250

def test_current_batch_completes_before_cancelled(db_pool: ConnectionPool, create_sentiment_service: SentimentService) -> None:
    """When cancel is triggered, current batch should complete processing before the worker exits"""
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            for i in range(3):
                cursor.execute("""
                    INSERT INTO raw_comments (
                        comment_id, post_id, comment_body, detected_products, subreddit,
                        author, score, created_utc, product_topic, sentiment_processed
                    ) VALUES (
                        %s, 'p1', 'Test comment', ARRAY['product1'],
                        'test_sub', 'test_author', 10, NOW(), 'GPU', FALSE
                    )
                """, (f"c{i}",))
    
    service = create_sentiment_service

    original_process = service._process_sentiment_and_write_to_db

    def trigger_shutdown_during_processing(*args: Any, **kwargs: Any) -> Any:
        service.cancel_requested = True
        return original_process(*args, **kwargs)

    with patch.object(service, '_process_sentiment_and_write_to_db',
                        side_effect=trigger_shutdown_during_processing):
        service._run_sentiment_pipeline()

    # Verify that the batch completed despite shutdown being triggered mid-processing
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM raw_comments WHERE sentiment_processed = TRUE")
            count = cursor.fetchone()
            assert count is not None
            assert count[0] == 3

            cursor.execute("SELECT COUNT(*) FROM product_sentiment")
            sentiment_count = cursor.fetchone()
            assert sentiment_count is not None
            assert sentiment_count[0] == 3
