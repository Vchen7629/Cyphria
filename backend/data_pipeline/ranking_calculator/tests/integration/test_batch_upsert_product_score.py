from datetime import timedelta
from datetime import timezone
from src.core.types import ProductScore
from src.db_utils.queries import batch_upsert_product_score
from datetime import datetime
import psycopg
import pytest

def test_upsert_one_product_score(db_connection: psycopg.Connection, single_product_score_comment: ProductScore) -> None:
    """One product score should be inserted properly into the database"""
    batch_upsert_product_score(db_connection, [single_product_score_comment])

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT product_name FROM product_rankings WHERE category = %s;",
            ("GPU",)
        )
        result = cursor.fetchone()

        assert result is not None
        assert len(result) == 1
        assert result[0] == "rtx 4090"

def test_upsert_updates_integer(db_connection: psycopg.Connection, single_product_score_comment: ProductScore) -> None:
    """Duplicate product score comment (product_name, time_window) with different mentions integer should be updated"""
    original_comment = single_product_score_comment

    batch_upsert_product_score(db_connection, [single_product_score_comment])

    upsert_comment = original_comment.model_copy()
    upsert_comment.mention_count = 200

    batch_upsert_product_score(db_connection, [upsert_comment])

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM product_rankings WHERE category = %s;",
            ("GPU",)
        )
        count = cursor.fetchone()
        assert count is not None
        assert count[0] == 1

        cursor.execute(
            "SELECT mention_count FROM product_rankings WHERE category = %s;",
            ("GPU",)
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 200

def test_upsert_updates_booleans(db_connection: psycopg.Connection, single_product_score_comment: ProductScore) -> None:
    """Duplicate product score comment (product_name, time_window) with different boolean value should be updated"""
    original_comment = single_product_score_comment

    batch_upsert_product_score(db_connection, [single_product_score_comment])

    upsert_comment = original_comment.model_copy()
    upsert_comment.is_top_pick = False
    upsert_comment.is_most_discussed = True
    upsert_comment.has_limited_data = True

    batch_upsert_product_score(db_connection, [upsert_comment])

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM product_rankings WHERE category = %s;",
            ("GPU",)
        )
        count = cursor.fetchone()
        assert count is not None
        assert count[0] == 1

        cursor.execute(
            "SELECT is_top_pick, is_most_discussed, has_limited_data FROM product_rankings WHERE category = %s;",
            ("GPU",)
        )
        result = cursor.fetchone()
        assert result is not None
        assert len(result) == 3
        assert not result[0]
        assert result[1]
        assert result[2]

def test_upsert_updates_floats(db_connection: psycopg.Connection, single_product_score_comment: ProductScore) -> None:
    """Duplicate product score comment (product_name, time_window) with different float value should be updated"""
    original_comment = single_product_score_comment

    batch_upsert_product_score(db_connection, [single_product_score_comment])

    upsert_comment = original_comment.model_copy()
    upsert_comment.bayesian_score = 0.21
    upsert_comment.avg_sentiment = 0.01

    batch_upsert_product_score(db_connection, [upsert_comment])

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM product_rankings WHERE category = %s;",
            ("GPU",)
        )
        count = cursor.fetchone()
        assert count is not None
        assert count[0] == 1

        cursor.execute(
            "SELECT bayesian_score, avg_sentiment FROM product_rankings WHERE category = %s;",
            ("GPU",)
        )
        result = cursor.fetchone()
        assert result is not None
        assert len(result) == 2
        assert result[0] == 0.21
        assert result[1] == 0.01

def test_upsert_updates_calculation_date(db_connection: psycopg.Connection, single_product_score_comment: ProductScore) -> None:
    """Duplicate product score comment (product_name, time_window) with different calculation date should be updated"""
    original_comment = single_product_score_comment

    batch_upsert_product_score(db_connection, [single_product_score_comment])

    upsert_comment = original_comment.model_copy()
    upsert_comment.calculation_date = datetime.now(timezone.utc) - timedelta(days=30)

    batch_upsert_product_score(db_connection, [upsert_comment])

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM product_rankings WHERE category = %s;",
            ("GPU",)
        )
        count = cursor.fetchone()
        assert count is not None
        assert count[0] == 1

        cursor.execute(
            "SELECT calculation_date FROM product_rankings WHERE category = %s;",
            ("GPU",)
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == (datetime.now(timezone.utc) - timedelta(days=30)).date()

def test_empty_product_score_comment_list(db_connection: psycopg.Connection) -> None:
    """Calling the sql query with no comment shouldn't update the database"""
    batch_upsert_product_score(db_connection, [])

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM product_rankings WHERE category = %s;",
            ("GPU",)
        )
        count = cursor.fetchone()
        assert count is not None
        assert count[0] == 0

def test_transaction_rollback_on_error(db_connection: psycopg.Connection, single_product_score_comment: ProductScore) -> None:
    """Transactions should be properly rolled back on error."""
    original_comment = single_product_score_comment

    batch_upsert_product_score(db_connection, [original_comment])

    # Commit the first insert so second error insert doesnt affect first valid insert
    db_connection.commit()

    invalid_comment = original_comment.model_copy()
    invalid_comment.product_name = None # type: ignore[assignment]: intentionally invalid for test
    invalid_comment.category = "Animals"
    
    with pytest.raises(psycopg.errors.NotNullViolation):
        batch_upsert_product_score(db_connection, [invalid_comment])
    
    db_connection.rollback()

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM product_rankings WHERE category = %s;", ("Animals",))
        count = cursor.fetchone()
        assert count is not None
        assert count[0] == 0

        cursor.execute("SELECT COUNT(*) FROM product_rankings WHERE category = %s;", ("GPU",))
        count = cursor.fetchone()
        assert count is not None
        assert count[0] == 1

def test_same_product_name_with_different_time_windows(db_connection: psycopg.Connection, single_product_score_comment: ProductScore) -> None:
    """The same product has both 90d and all_time time windows"""
    all_time = single_product_score_comment

    ninety_day = all_time.model_copy()
    ninety_day.time_window = "90d"

    batch_upsert_product_score(db_connection, [all_time, ninety_day])

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM product_rankings WHERE category = %s;", ("GPU",))
        count = cursor.fetchone()
        assert count is not None
        assert count[0] == 2

        cursor.execute("SELECT time_window FROM product_rankings WHERE category = %s;", ("GPU",))
        results = cursor.fetchall()
        assert results is not None
        assert results[0][0] == "all_time"
        assert results[1][0] == "90d"

def test_mixed_batch_with_duplicates(db_connection: psycopg.Connection, single_product_score_comment: ProductScore) -> None:
    """Batch insert a mix of new and duplicate product score comments"""
    original_comment = single_product_score_comment
    
    duplicate_one = original_comment.model_copy()
    duplicate_one.mention_count = 200

    duplicate_two = original_comment.model_copy()
    duplicate_two.mention_count = 300

    new_one = original_comment.model_copy()
    new_one.product_name = "rtx 5070"
    new_one.mention_count = 250
    
    new_two = original_comment.model_copy()
    new_two.product_name = "rtx 5080"
    new_two.mention_count = 350

    batch_upsert_product_score(db_connection, [original_comment, duplicate_one, duplicate_two, new_one, new_two])

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM product_rankings WHERE category = %s;", ("GPU",))
        count = cursor.fetchone()
        assert count is not None
        assert count[0] == 3

        cursor.execute("SELECT mention_count, product_name FROM product_rankings WHERE category = %s;", ("GPU",))
        results = cursor.fetchall()
        assert results is not None
        assert results[0] == (300, "rtx 4090") # last duplicate upserted and updated it to 300
        assert results[1] == (250, "rtx 5070")
        assert results[2] == (350, "rtx 5080")

