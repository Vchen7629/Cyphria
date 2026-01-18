import os
import psycopg
import pytest
from datetime import datetime, timezone
from typing import Generator
from unittest.mock import Mock, patch
from psycopg_pool import ConnectionPool
from testcontainers.postgres import PostgresContainer

os.environ['PRODUCT_CATEGORY'] = 'GPU'

from src.worker import IngestionService
from src.preprocessing.relevant_fields import RedditComment
from src.core.logger import StructuredLogger
from src.product_utils.detector_factory import DetectorFactory
from src.product_utils.normalizer_factory import NormalizerFactory
from src.db_utils.queries import batch_insert_raw_comments


@pytest.fixture
def mock_reddit_client() -> Mock:
    """Mock Reddit client to avoid actual API calls."""
    return Mock()


@pytest.fixture
def worker_with_test_db(postgres_container: PostgresContainer, mock_reddit_client: Mock) -> Generator[IngestionService, None, None]:
    """
    Create a Worker instance configured to use the test database.
    Patches the connection pool to use the test container.
    """
    with patch('src.core.reddit_client_instance.createRedditClient', return_value=mock_reddit_client) as mock_reddit_client:
        with patch('src.db_utils.conn.create_connection_pool') as mock_pool:
            # Create a real connection pool to the test database
            # Convert SQLAlchemy URL to PostgreSQL URI for psycopg
            connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
            test_pool = ConnectionPool(
                conninfo=connection_url,
                min_size=1,
                max_size=5,
                open=True
            )
            mock_pool.return_value = test_pool

            worker = IngestionService(
                reddit_client=mock_reddit_client,
                db_pool=test_pool,
                logger=StructuredLogger(pod="ingestion_service"),
                category="gpu",
                subreddits=["nvidia"],
                detector=DetectorFactory.get_detector("gpu"),
                normalizer=NormalizerFactory
            )
            yield worker

            # Cleanup - truncate table after test
            with test_pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE raw_comments RESTART IDENTITY CASCADE;")
                conn.commit()

            test_pool.close()

def test_worker_reddit_comment_to_db_conversion(worker_with_test_db: IngestionService, postgres_container: PostgresContainer) -> None:
    """
    Test that Worker._batch_insert_to_db correctly converts RedditComment objects
    to the dict format expected by batch_insert_raw_comments.
    """
    comment = RedditComment(
        comment_id='conversion_test_1',
        post_id='post_1',
        comment_body='Test comment about RTX 4090',
        detected_products=['rtx 4090', 'rtx 4080'],
        subreddit='nvidia',
        author='test_user',
        score=100,
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    worker_with_test_db._batch_insert_to_db([comment])

    # Verify all fields were correctly mapped
    # Convert SQLAlchemy URL to PostgreSQL URI for psycopg
    connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
    with psycopg.connect(connection_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM raw_comments WHERE comment_id = %s;", ('conversion_test_1',))
            result = cursor.fetchone()

            assert result is not None
            assert result[1] == 'conversion_test_1'  # comment_id
            assert result[2] == 'post_1'  # post_id
            assert result[3] == 'Test comment about RTX 4090'  # comment_body
            assert result[4] == ['rtx 4090', 'rtx 4080']  # detected_products
            assert result[5] == 'nvidia'  # subreddit
            assert result[6] == 'test_user'  # author
            assert result[7] == 100  # score
            assert result[8] == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)  # created_utc
            assert result[9] == "gpu" # category


def test_worker_injects_category_field(worker_with_test_db: IngestionService, postgres_container: PostgresContainer) -> None:
    """
    Test that Worker._batch_insert_to_db correctly injects the category field
    from the worker's configuration (not present in RedditComment).
    """
    comment = RedditComment(
        comment_id='category_injection_test',
        post_id='post_1',
        comment_body='Test comment',
        detected_products=['rtx 4090'],
        subreddit='nvidia',
        author='test_user',
        score=50,
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    )

    # RedditComment doesn't have a category field
    assert not hasattr(comment, 'category')

    worker_with_test_db._batch_insert_to_db([comment])

    # Verify the category was injected from the worker's config
    # Convert SQLAlchemy URL to PostgreSQL URI for psycopg
    connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
    with psycopg.connect(connection_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT category FROM raw_comments WHERE comment_id = %s;", ('category_injection_test',))
            result = cursor.fetchone()
            assert result is not None
            category = result[0]
            assert category == worker_with_test_db.category

def test_worker_batch_insert_error_handling(worker_with_test_db: IngestionService) -> None:
    """Test that Worker properly propagates database errors during batch insert."""
    invalid_data = [{
        'comment_id': 'invalid_test',
        'post_id': 'post_1',
        'comment_body': None, # type: ignore
        'detected_products': ['rtx 4090'],
        'subreddit': 'nvidia',
        'author': 'user1',
        'score': 10,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'category': worker_with_test_db.category
    }]

    # This should raise a NotNullViolation error from the database
    with pytest.raises(psycopg.errors.NotNullViolation):
        with worker_with_test_db.db_pool.connection() as conn:
            batch_insert_raw_comments(conn, invalid_data)

def test_worker_batch_insert_with_connection_pool_multiple_batches(worker_with_test_db: IngestionService, postgres_container: PostgresContainer) -> None:
    """
    Test that Worker can handle multiple sequential batch inserts using the connection pool.
    This simulates the actual worker flow where batches are inserted as they fill up.
    """
    # First batch
    batch1 = [
        RedditComment(
            comment_id=f'batch1_{i}',
            post_id=f'post_{i}',
            comment_body=f'Batch 1 comment {i}',
            detected_products=['rtx 4090'],
            subreddit='nvidia',
            author=f'user_{i}',
            score=i,
            timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )
        for i in range(5)
    ]

    # Second batch
    batch2 = [
        RedditComment(
            comment_id=f'batch2_{i}',
            post_id=f'post_{i}',
            comment_body=f'Batch 2 comment {i}',
            detected_products=['rtx 4080'],
            subreddit='nvidia',
            author=f'user_{i}',
            score=i,
            timestamp=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
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
