from typing import Any
import threading
from src.worker import StartService
from psycopg_pool.pool import ConnectionPool
from src.db_utils.queries import mark_comments_processed
from src.db_utils.queries import batch_insert_product_sentiment
from src.core.types import ProductSentiment
from unittest.mock import patch, MagicMock
import psycopg
import signal
import time
from datetime import datetime, timezone

def test_shutdown_flag_stops_worker_loop(db_pool: ConnectionPool) -> None:
    """Shutdown_requested flag should cause worker loop to exit properly"""
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            for i in range(10):
                cursor.execute("""
                    INSERT INTO raw_comments (
                        comment_id, post_id, comment_body, detected_products, subreddit,
                        author, score, created_utc, category, sentiment_processed
                    ) VALUES (
                        %s, 'p1', 'Test comment', ARRAY['product1'],
                        'test_sub', 'test_author', 10, NOW(), 'crypto', FALSE
                    )
                """, (f"c{i}",))

    with patch.object(StartService, '_database_conn_lifespan'), \
         patch.object(StartService, '_initialize_absa_model'), \
         patch.object(StartService, '_cleanup'): 

        service = StartService()
        service.db_pool = db_pool

        # Mock ABSA to return correct number of sentiment results based on input
        mock_absa_instance = MagicMock()
        def mock_sentiment_analysis(pairs: list[tuple[str, str]]) -> list[tuple[None, float]]:
            # Return one sentiment result per input pair
            return [(None, 0.8) for _ in pairs]
        mock_absa_instance.SentimentAnalysis.side_effect = mock_sentiment_analysis
        service.ABSA = mock_absa_instance

        # Use seperate thread to trigger shutdown to prevent blocking
        def trigger_shutdown() -> None:
            time.sleep(0.5) # short delay so worker can process at least one batch
            service.shutdown_requested = True

        shutdown_thread = threading.Thread(target=trigger_shutdown, daemon=True)
        shutdown_thread.start()

        service.run()

        assert service.shutdown_requested is True

        # verify that some comments were processed before shutdown
        with db_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM raw_comments WHERE sentiment_processed = TRUE")

                count = cursor.fetchone()
                assert count is not None
                assert count[0] > 0

def test_cleanup_called_on_shutdown(db_pool: ConnectionPool) -> None:
    """Cleanup method should be called when worker shuts down"""
    with patch.object(StartService, '_database_conn_lifespan'), \
         patch.object(StartService, '_initialize_absa_model'):

        service = StartService()
        service.db_pool = db_pool

        mock_absa_instance = MagicMock()
        service.ABSA = mock_absa_instance

        service.shutdown_requested = True

        # Mock cleanup without wrapping to prevent pool closure
        with patch.object(service, '_cleanup') as mock_cleanup:
            service.run()

            mock_cleanup.assert_called_once()

def test_no_data_loss_when_shutdown_between_batches(db_pool: ConnectionPool) -> None:
    """
    Shutting down between batches shouln't cause data loss.
    All processed comments should be properly marked
    """
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            for i in range(250):
                cursor.execute("""
                    INSERT INTO raw_comments (
                        comment_id, post_id, comment_body, detected_products, subreddit,
                        author, score, created_utc, category, sentiment_processed
                    ) VALUES (
                        %s, 'p1', 'Test comment', ARRAY['product1'],
                        'test_sub', 'test_author', 10, NOW(), 'crypto', FALSE
                    )
                """, (f"c{i}",))

    with patch.object(StartService, '_database_conn_lifespan'), \
         patch.object(StartService, '_initialize_absa_model'), \
         patch.object(StartService, '_cleanup'):

        service = StartService()
        service.db_pool = db_pool

        # Mock ABSA to return correct number of sentiment results based on input
        mock_absa_instance = MagicMock()
        def mock_sentiment_analysis(pairs: list[tuple[str, str]]) -> list[tuple[None, float]]:
            # Return one sentiment result per input pair
            return [(None, 0.8) for _ in pairs]
        mock_absa_instance.SentimentAnalysis.side_effect = mock_sentiment_analysis
        service.ABSA = mock_absa_instance

        # Track how many batches have been processed
        original_process_comments = service._process_comments
        batch_count = {"count": 0}

        def track_batches(comments: list[Any]) -> tuple[int, int]:
            result = original_process_comments(comments)
            batch_count["count"] += 1

            if batch_count["count"] == 1:
                service.shutdown_requested = True
            return result

        with patch.object(service, '_process_comments', side_effect=track_batches):
            service.run()

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

def test_current_batch_completes_before_shutdown(db_pool: ConnectionPool) -> None:
    """
    When shutdown is triggered, current batch should
    complete processing before the worker exits
    """
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            for i in range(3):
                cursor.execute("""
                    INSERT INTO raw_comments (
                        comment_id, post_id, comment_body, detected_products, subreddit,
                        author, score, created_utc, category, sentiment_processed
                    ) VALUES (
                        %s, 'p1', 'Test comment', ARRAY['product1'],
                        'test_sub', 'test_author', 10, NOW(), 'crypto', FALSE
                    )
                """, (f"c{i}",))
    
    with patch.object(StartService, '_database_conn_lifespan'), \
         patch.object(StartService, '_initialize_absa_model'), \
         patch.object(StartService, '_cleanup'):

        service = StartService()
        service.db_pool = db_pool

        # Mock ABSA to return correct number of sentiment results based on input
        mock_absa_instance = MagicMock()
        def mock_sentiment_analysis(pairs: list[tuple[str, str]]) -> list[tuple[None, float]]:
            # Return one sentiment result per input pair
            return [(None, 0.8) for _ in pairs]
        mock_absa_instance.SentimentAnalysis.side_effect = mock_sentiment_analysis
        service.ABSA = mock_absa_instance

        original_process = service._process_sentiment_and_write_to_db

        def trigger_shutdown_during_processing(*args: Any, **kwargs: Any) -> Any:
            service.shutdown_requested = True
            return original_process(*args, **kwargs)

        with patch.object(service, '_process_sentiment_and_write_to_db',
                          side_effect=trigger_shutdown_during_processing):
            service.run()

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
        