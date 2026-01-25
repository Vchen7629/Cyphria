import psycopg
import pytest
from datetime import datetime
from datetime import timezone
from src.api.schemas import ProductSentiment
from src.db_utils.queries import batch_insert_product_sentiment

def test_single_sentiment_insert(db_connection: psycopg.Connection) -> None:
    """Inserting a single product sentiment into the database should be returned."""
    sentiment = ProductSentiment(
        comment_id='test_comment_1',
        product_name='rtx 4090',
        product_topic="GPU",
        sentiment_score=0.85,
        created_utc='2024-01-01T12:00:00+00:00'
    )

    rows_inserted = batch_insert_product_sentiment(db_connection, [sentiment])

    assert rows_inserted == 1

    # Verify the insert
    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT comment_id, product_name, product_topic, sentiment_score, created_utc FROM product_sentiment WHERE comment_id = %s;",
            ('test_comment_1',)
        )
        result = cursor.fetchone()

        assert result is not None
        assert result[0] == 'test_comment_1'  # comment_id
        assert result[1] == 'rtx 4090'  # product_name
        assert result[2] == 'GPU' # product_topic
        assert result[3] == 0.85  # sentiment_score
        assert result[4].isoformat() == '2024-01-01T12:00:00+00:00'  # created_utc

def test_batch_insert_large_batch(db_connection: psycopg.Connection) -> None:
    """Batch inserting a large number of comments (100+) shouldnt error."""
    sentiments = [
        ProductSentiment(
            comment_id=f'test_comment_{i}',
            product_name='rtx 4090',
            product_topic="GPU",
            sentiment_score=0.5 + (i * 0.1),
            created_utc=datetime(2024, 1, 1, 12, 59, 0, tzinfo=timezone.utc)
        )
        for i in range(150)
    ]

    batch_insert_product_sentiment(db_connection, sentiments)

    # Verify all comments were inserted
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM product_sentiment;")
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 150

def test_duplicate_comment_handling(db_connection: psycopg.Connection) -> None:
    """Duplicate (comment_ids, product_names) are ignored (ON CONFLICT DO NOTHING)."""
    sentiment = ProductSentiment(
        comment_id='duplicate_id',
        product_name='rtx 4090',
        product_topic="GPU",
        sentiment_score=0.85,
        created_utc='2024-01-01T12:00:00+00:00'
    )

    # Insert the first time
    batch_insert_product_sentiment(db_connection, [sentiment])

    # Try to insert duplicate with different data
    duplicate_comment = sentiment.model_copy()
    duplicate_comment.sentiment_score = 0.99

    # Should not raise an error
    batch_insert_product_sentiment(db_connection, [duplicate_comment])

    # Verify only one comment exists and it has the original data
    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) \
            FROM product_sentiment \
            WHERE (comment_id, product_name) = (%s, %s);"
        , ('duplicate_id', 'rtx 4090'))
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 1

        cursor.execute(
            "SELECT sentiment_score \
            FROM product_sentiment \
            WHERE (comment_id, product_name) = (%s, %s);"
        , ('duplicate_id', 'rtx 4090'))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 0.85  # Original score preserved

def test_empty_comments_list(db_connection: psycopg.Connection) -> None:
    """Passing an empty list shouldn't cause errors."""
    batch_insert_product_sentiment(db_connection, [])

    # Verify no comments were inserted
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM product_sentiment;")
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 0

def test_transaction_rollback_on_error(db_connection: psycopg.Connection) -> None:
    """Transactions should be properly rolled back on error."""
    sentiment = ProductSentiment(
        comment_id='success_1',
        product_name='rtx 4090',
        product_topic="GPU",
        sentiment_score=0.85,
        created_utc='2024-01-01T12:00:00+00:00'
    )

    batch_insert_product_sentiment(db_connection, [sentiment])

    # Commit the first insert so second error insert doesnt affect first valid insert
    db_connection.commit()

    invalid_sentiment = ProductSentiment.model_construct(
        comment_id='invalid',
        product_name='rtx 4090',
        product_topic="GPU",
        sentiment_score=None, # type: ignore
        created_utc='2024-01-01T12:00:00+00:00'
    )

    with pytest.raises(psycopg.errors.NotNullViolation):
        batch_insert_product_sentiment(db_connection, [invalid_sentiment])

    # Rollback the failed transaction before running verification queries
    db_connection.rollback()

    # Verify the invalid comment was not inserted
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM product_sentiment WHERE comment_id = %s;", ('invalid',))
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 0

        # But the valid comment should still be there
        cursor.execute("SELECT COUNT(*) FROM product_sentiment WHERE comment_id = %s;", ('success_1',))
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 1

def test_same_comment_id_with_different_product_names(db_connection: psycopg.Connection) -> None:
    """One comment id may have multiple product names"""
    initial = ProductSentiment(
        comment_id='initial',
        product_name='rtx 4090',
        product_topic="GPU",
        sentiment_score=0.85,
        created_utc='2024-01-01T12:00:00+00:00'
    )

    batch_insert_product_sentiment(db_connection, [initial])

    different_product_batch = [
        ProductSentiment(
            comment_id='initial',
            product_name='rtx 5090',
            product_topic="GPU",
            sentiment_score=0.85,
            created_utc='2024-01-01T12:00:00+00:00'
        ),
        ProductSentiment(
            comment_id='initial',
            product_name='rtx 5070',
            product_topic="GPU",
            sentiment_score=0.85,
            created_utc='2024-01-01T12:00:00+00:00'
        )
    ]

    batch_insert_product_sentiment(db_connection, different_product_batch)

    # Verify that all 3 rows were inserted
    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) \
            FROM product_sentiment \
            WHERE comment_id = %s;"
        , ('initial',))
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 3

        cursor.execute(
            "SELECT product_name, sentiment_score, product_topic \
            FROM product_sentiment \
            WHERE comment_id = %s;"
        , ('initial',))
        result = cursor.fetchall()
        assert result is not None
        assert result[0] == ("rtx 4090", 0.85, "GPU")
        assert result[1] == ("rtx 5070", 0.85, "GPU")
        assert result[2] == ("rtx 5090", 0.85, "GPU")

def test_mixed_batch_with_duplicates(db_connection: psycopg.Connection) -> None:
    """Batch insert with mix of new and duplicate comments."""
    initial_sentiment = ProductSentiment(
        comment_id='initial',
        product_name='rtx 4090',
        product_topic="GPU",
        sentiment_score=0.85,
        created_utc='2024-01-01T12:00:00+00:00'
    )

    batch_insert_product_sentiment(db_connection, [initial_sentiment])

    # Batch with mix of new and duplicate
    mixed_batch = [
        ProductSentiment(
            comment_id='initial',
            product_name='rtx 4090',
            product_topic="GPU",
            sentiment_score=0.85,
            created_utc='2024-01-01T12:00:00+00:00'
        ),
        ProductSentiment(
            comment_id='new',
            product_name='rtx 4090',
            product_topic="GPU",
            sentiment_score=0.87,
            created_utc='2024-01-01T12:00:00+00:00'
        ),
        ProductSentiment(
            comment_id='new_2',
            product_name='rtx 5090',
            product_topic="GPU",
            sentiment_score=0.89,
            created_utc='2024-01-01T12:00:00+00:00'
        ),
    ]

    batch_insert_product_sentiment(db_connection, mixed_batch)

    # Verify: should have 3 total comments (1 original + 2 new, duplicate ignored)
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM product_sentiment;")
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 3

        # Verify the duplicate kept original data
        cursor.execute(
            "SELECT sentiment_score, product_topic \
            FROM product_sentiment \
            WHERE (comment_id, product_name) = (%s, %s);"
        , ('initial', 'rtx 4090'))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 0.85
        assert result[1] == 'GPU'

def test_boundary_sentiment_scores(db_connection: psycopg.Connection) -> None:
    """Boundary sentiment score values like -1.0, 0.0, and 1.0 should work"""
    # Batch with boundary comments
    boundary_batch = [
        ProductSentiment(
            comment_id='negative',
            product_name='rtx 4090',
            product_topic="GPU",
            sentiment_score=-1.0,
            created_utc='2024-01-01T12:00:00+00:00'
        ),
        ProductSentiment(
            comment_id='middle',
            product_name='rtx 4090',
            product_topic="GPU",
            sentiment_score=0.0,
            created_utc='2024-01-01T12:00:00+00:00'
        ),
        ProductSentiment(
            comment_id='positive',
            product_name='rtx 4090',
            product_topic="GPU",
            sentiment_score=1.0,
            created_utc='2024-01-01T12:00:00+00:00'
        ),
    ]

    batch_insert_product_sentiment(db_connection, boundary_batch)

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM product_sentiment;")
        result = cursor.fetchone()
        assert result is not None
        count = result[0]
        assert count == 3

        cursor.execute(
            "SELECT comment_id, sentiment_score, product_topic \
            FROM product_sentiment \
            WHERE product_name = %s;"
        , ('rtx 4090',))
        result = cursor.fetchall()
        assert result is not None
        assert result[0] == ("negative", -1.0, 'GPU')
        assert result[1] == ("middle", 0.0, 'GPU')
        assert result[2] == ("positive", 1.0, 'GPU')
