from typing import Any
from psycopg_pool import ConnectionPool
from src.db_utils.queries import batch_insert_raw_comments
import psycopg
import pytest

def test_connection_pool_creation(db_pool: ConnectionPool) -> None:
    """Test that connection pool is created successfully and can acquire connections."""
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            assert result == (1,)

def test_single_comment_insert(
    db_connection: psycopg.Connection, 
    mock_raw_comment: dict[str, Any]
) -> None:
    """Test inserting a single comment into the database."""
    batch_insert_raw_comments(db_connection, [mock_raw_comment])

    # Verify the insert
    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT * \
            FROM raw_comments \
            WHERE comment_id = %s;", 
        ('test_comment_1',))
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

def test_batch_insert_multiple_comments(
    db_connection: psycopg.Connection,
    mock_raw_comment: dict[str, Any]
) -> None:
    """Test batch inserting multiple comments."""
    comments = [
        {**mock_raw_comment, "comment_id": f"test_comment_{i}"}
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


def test_batch_insert_large_batch(
    db_connection: psycopg.Connection,
    mock_raw_comment: dict[str, Any]
) -> None:
    """Test batch inserting a large number of comments (100+)."""
    comments = [
        {**mock_raw_comment, 'comment_id': f'test_comment_{i}'}
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


def test_duplicate_comment_handling(
    db_connection: psycopg.Connection,
    mock_raw_comment: dict[str, Any]
) -> None:
    """Test that duplicate comment_ids are ignored (ON CONFLICT DO NOTHING)."""
    comment = {**mock_raw_comment, "comment_id": "duplicate_test", "comment_body": "Original comment", "score": 10}

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


def test_multiple_products_detected(
    db_connection: psycopg.Connection,
    mock_raw_comment: dict[str, Any]
) -> None:
    """Test inserting a comment with multiple detected products."""
    comment = {**mock_raw_comment, 'comment_id': 'multi_product_test', 'detected_products': ['rtx 4090', 'rtx 4080', 'rtx 3090']}

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

def test_transaction_rollback_on_error(
    db_connection: psycopg.Connection,
    mock_raw_comment: dict[str, Any]
) -> None:
    """Test that transactions are properly rolled back on error."""
    comment = {**mock_raw_comment, 'comment_id': 'test_rollback'}

    # Insert successfully first
    batch_insert_raw_comments(db_connection, [comment])

    # Create an invalid comment by setting a NOT NULL field to None
    invalid_comment = {**mock_raw_comment, 'comment_id': 'test_invalid', 'comment_body': None}

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


def test_mixed_batch_with_duplicates(
    db_connection: psycopg.Connection,
    mock_raw_comment: dict[str, Any]
) -> None:
    """Test batch insert with mix of new and duplicate comments."""
    # Insert initial comment
    initial_comment = {**mock_raw_comment,'comment_id': 'existing_comment', 'score': 10}
    batch_insert_raw_comments(db_connection, [initial_comment])

    # Batch with mix of new and duplicate
    mixed_batch = [
        {**mock_raw_comment, 'comment_id': 'existing_comment', 'score': 99}, # Duplicate
        {**mock_raw_comment, 'comment_id': 'new_comment_1', 'score': 20}, # New 1
        {**mock_raw_comment, 'comment_id': 'new_comment_2', 'score': 30}  # New 2
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
        assert result[0] == 'This is a test comment about RTX 4090'
        assert result[1] == 10
