import psycopg
import pytest
from datetime import datetime, timezone
from psycopg_pool import ConnectionPool

from src.db_utils.queries import batch_insert_raw_comments

def test_connection_pool_creation(db_pool: ConnectionPool) -> None:
    """Test that connection pool is created successfully and can acquire connections."""
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            assert result == (1,)


def test_single_comment_insert(db_connection: psycopg.Connection) -> None:
    """Test inserting a single comment into the database."""
    comment = {
        'comment_id': 'test_comment_1',
        'post_id': 'test_post_1',
        'comment_body': 'This is a test comment about RTX 4090',
        'detected_products': ['rtx 4090'],
        'subreddit': 'nvidia',
        'author': 'test_user',
        'score': 42,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'category': 'GPU'
    }

    batch_insert_raw_comments(db_connection, [comment])

    # Verify the insert
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT * FROM raw_comments WHERE comment_id = %s;", ('test_comment_1',))
        result = cursor.fetchone()

        assert result is not None
        assert result[1] == 'test_comment_1'  # comment_id
        assert result[2] == 'test_post_1'  # post_id
        assert result[3] == 'This is a test comment about RTX 4090'  # comment_body
        assert result[4] == ['rtx 4090']  # detected_products
        assert result[5] == 'nvidia'  # subreddit
        assert result[6] == 'test_user'  # author
        assert result[7] == 42  # score
        assert result[9] == 'GPU'  # category
        assert result[11] is False  # sentiment_processed

def test_batch_insert_multiple_comments(db_connection: psycopg.Connection) -> None:
    """Test batch inserting multiple comments."""
    comments = [
        {
            'comment_id': f'test_comment_{i}',
            'post_id': f'test_post_{i}',
            'comment_body': f'Test comment {i}',
            'detected_products': ['rtx 4090'],
            'subreddit': 'nvidia',
            'author': f'user_{i}',
            'score': i * 10,
            'created_utc': datetime(2024, 1, 1, 12, i, 0, tzinfo=timezone.utc),
            'category': 'GPU'
        }
        for i in range(1, 6)
    ]

    batch_insert_raw_comments(db_connection, comments)

    # Verify all comments were inserted
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM raw_comments;")
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 5


def test_batch_insert_large_batch(db_connection: psycopg.Connection) -> None:
    """Test batch inserting a large number of comments (100+)."""
    comments = [
        {
            'comment_id': f'test_comment_{i}',
            'post_id': f'test_post_{i}',
            'comment_body': f'Test comment {i}',
            'detected_products': ['rtx 4090', 'rtx 5090'],
            'subreddit': 'nvidia',
            'author': f'user_{i}',
            'score': i,
            'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'category': 'GPU'
        }
        for i in range(150)
    ]

    batch_insert_raw_comments(db_connection, comments)

    # Verify all comments were inserted
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM raw_comments;")
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 150


def test_duplicate_comment_handling(db_connection: psycopg.Connection) -> None:
    """Test that duplicate comment_ids are ignored (ON CONFLICT DO NOTHING)."""
    comment = {
        'comment_id': 'duplicate_test',
        'post_id': 'test_post_1',
        'comment_body': 'Original comment',
        'detected_products': ['rtx 4090'],
        'subreddit': 'nvidia',
        'author': 'user1',
        'score': 10,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'category': 'GPU'
    }

    # Insert the first time
    batch_insert_raw_comments(db_connection, [comment])

    # Try to insert duplicate with different data
    duplicate_comment = comment.copy()
    duplicate_comment['comment_body'] = 'Modified comment'
    duplicate_comment['score'] = 999

    # Should not raise an error
    batch_insert_raw_comments(db_connection, [duplicate_comment])

    # Verify only one comment exists and it has the original data
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM raw_comments WHERE comment_id = %s;", ('duplicate_test',))
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 1

        cursor.execute("SELECT comment_body, score FROM raw_comments WHERE comment_id = %s;", ('duplicate_test',))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 'Original comment'  # Original body preserved
        assert result[1] == 10  # Original score preserved


def test_empty_comments_list(db_connection: psycopg.Connection) -> None:
    """Test that passing an empty list doesn't cause errors."""
    batch_insert_raw_comments(db_connection, [])

    # Verify no comments were inserted
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM raw_comments;")
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 0


def test_multiple_products_detected(db_connection: psycopg.Connection) -> None:
    """Test inserting a comment with multiple detected products."""
    comment = {
        'comment_id': 'multi_product_test',
        'post_id': 'test_post_1',
        'comment_body': 'I have RTX 4090 and RTX 4080',
        'detected_products': ['rtx 4090', 'rtx 4080', 'rtx 3090'],
        'subreddit': 'nvidia',
        'author': 'user1',
        'score': 50,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'category': 'GPU'
    }

    batch_insert_raw_comments(db_connection, [comment])

    # Verify the products array
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT detected_products FROM raw_comments WHERE comment_id = %s;", ('multi_product_test',))
        result = cursor.fetchone()
        assert result is not None
        assert len(result[0]) == 3
        assert 'rtx 4090' in result[0]
        assert 'rtx 4080' in result[0]
        assert 'rtx 3090' in result[0]


def test_connection_failure_handling() -> None:
    """Test handling of connection failures with invalid connection string."""
    invalid_conninfo = "host=invalid_host port=9999 dbname=invalid user=invalid password=invalid"

    with pytest.raises(psycopg.OperationalError):
        conn = psycopg.connect(invalid_conninfo, connect_timeout=1)
        conn.close()


def test_pool_multiple_connections(db_pool: ConnectionPool) -> None:
    """Test that connection pool can handle multiple concurrent connections."""
    connections = []

    try:
        # Acquire multiple connections
        for _ in range(3):
            conn = db_pool.getconn()
            connections.append(conn)

            # Test each connection works
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()
                assert result == (1,)
    finally:
        # Return all connections to pool
        for conn in connections:
            db_pool.putconn(conn)


def test_transaction_rollback_on_error(db_connection: psycopg.Connection) -> None:
    """Test that transactions are properly rolled back on error."""
    comment = {
        'comment_id': 'test_rollback',
        'post_id': 'test_post_1',
        'comment_body': 'Test comment',
        'detected_products': ['rtx 4090'],
        'subreddit': 'nvidia',
        'author': 'user1',
        'score': 10,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'category': 'GPU'
    }

    # Insert successfully first
    batch_insert_raw_comments(db_connection, [comment])

    invalid_comment = {
        'comment_id': 'test_invalid',
        'post_id': 'test_post_2',
        'comment_body': None, # type: ignore
        'detected_products': ['rtx 4090'],
        'subreddit': 'nvidia',
        'author': 'user2',
        'score': 20,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'category': 'GPU'
    }

    with pytest.raises(psycopg.errors.NotNullViolation):
        batch_insert_raw_comments(db_connection, [invalid_comment])

    # Rollback the failed transaction before running verification queries
    db_connection.rollback()

    # Verify the invalid comment was not inserted
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM raw_comments WHERE comment_id = %s;", ('test_invalid',))
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 0

        # But the valid comment should still be there
        cursor.execute("SELECT COUNT(*) FROM raw_comments WHERE comment_id = %s;", ('test_rollback',))
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 1


def test_mixed_batch_with_duplicates(db_connection: psycopg.Connection) -> None:
    """Test batch insert with mix of new and duplicate comments."""
    # Insert initial comment
    initial_comment = {
        'comment_id': 'existing_comment',
        'post_id': 'test_post_1',
        'comment_body': 'Existing comment',
        'detected_products': ['rtx 4090'],
        'subreddit': 'nvidia',
        'author': 'user1',
        'score': 10,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'category': 'GPU'
    }
    batch_insert_raw_comments(db_connection, [initial_comment])

    # Batch with mix of new and duplicate
    mixed_batch = [
        {
            'comment_id': 'existing_comment',  # Duplicate
            'post_id': 'test_post_1',
            'comment_body': 'Modified',
            'detected_products': ['rtx 5090'],
            'subreddit': 'nvidia',
            'author': 'user1',
            'score': 999,
            'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'category': 'GPU'
        },
        {
            'comment_id': 'new_comment_1',  # New
            'post_id': 'test_post_2',
            'comment_body': 'New comment 1',
            'detected_products': ['rtx 4080'],
            'subreddit': 'nvidia',
            'author': 'user2',
            'score': 20,
            'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'category': 'GPU'
        },
        {
            'comment_id': 'new_comment_2',  # New
            'post_id': 'test_post_3',
            'comment_body': 'New comment 2',
            'detected_products': ['rtx 3090'],
            'subreddit': 'nvidia',
            'author': 'user3',
            'score': 30,
            'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'category': 'GPU'
        }
    ]

    batch_insert_raw_comments(db_connection, mixed_batch)

    # Verify: should have 3 total comments (1 original + 2 new, duplicate ignored)
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM raw_comments;")
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 3

        # Verify the duplicate kept original data
        cursor.execute("SELECT comment_body, score FROM raw_comments WHERE comment_id = %s;", ('existing_comment',))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 'Existing comment'
        assert result[1] == 10
