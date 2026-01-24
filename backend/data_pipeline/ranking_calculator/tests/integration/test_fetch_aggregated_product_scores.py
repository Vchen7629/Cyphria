from typing import Any
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from src.db.queries import fetch_aggregated_product_scores
import psycopg

def test_fetch_single_comment_comment(db_connection: psycopg.Connection, single_sentiment_comment: dict[str, Any]) -> None:
    """Fetching a single comment from the database should return the correct values"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO product_sentiment (
                comment_id, product_name, category, sentiment_score, created_utc
            ) VALUES (
                %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
            )
        """, single_sentiment_comment)

    result = fetch_aggregated_product_scores(db_connection, category="GPU", time_window="all_time")

    assert len(result) == 1
    assert result[0].product_name == 'rtx 4090'
    assert result[0].avg_sentiment == 0.89
    assert result[0].mention_count == 1
    assert result[0].positive_count == 1
    assert result[0].negative_count == 0
    assert result[0].neutral_count == 0
    assert result[0].approval_percentage == 100

def test_fetches_posts_90_days_old_but_not_older(db_connection: psycopg.Connection) -> None:
    comments = [
        {
            'comment_id': 'test_comment_1',
            'product_name': 'rtx 4090',
            'category': 'GPU',
            'sentiment_score': 0.89,
            'created_utc': datetime.now()
        },
        {
            'comment_id': 'test_comment_2',
            'product_name': 'rtx 5090',
            'category': 'GPU',
            'sentiment_score': 0.89,
            'created_utc': datetime(1999, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        }
    ]

    with db_connection.cursor() as cursor:
        for comment in comments:
            cursor.execute("""
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """, comment)

    result = fetch_aggregated_product_scores(db_connection, category="GPU", time_window="90d")

    assert len(result) == 1
    assert result[0].product_name == 'rtx 4090'
    assert result[0].avg_sentiment == 0.89
    assert result[0].mention_count == 1
    assert result[0].positive_count == 1
    assert result[0].negative_count == 0
    assert result[0].neutral_count == 0
    assert result[0].approval_percentage == 100

def test_fetches_sentiment_comments_sentiment_score_desc(db_connection: psycopg.Connection) -> None:
    """It should fetch the comments with avg sentiment descending"""
    comments = [
        {
            'comment_id': 'test_comment_1',
            'product_name': 'rtx 4070',
            'category': 'GPU',
            'sentiment_score': 0.20,
            'created_utc': datetime.now()
        },
        {
            'comment_id': 'test_comment_2',
            'product_name': 'rtx 4080',
            'category': 'GPU',
            'sentiment_score': 0.60,
            'created_utc': datetime.now()
        },
        {
            'comment_id': 'test_comment_3',
            'product_name': 'rtx 4090',
            'category': 'GPU',
            'sentiment_score': 0.89,
            'created_utc': datetime.now()
        }
    ]

    with db_connection.cursor() as cursor:
        for comment in comments:
            cursor.execute("""
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """, comment)
        
    result = fetch_aggregated_product_scores(db_connection, category="GPU", time_window="all_time")

    assert len(result) == 3
    assert result[0].product_name == 'rtx 4090'
    assert result[1].product_name == 'rtx 4080'
    assert result[2].product_name == 'rtx 4070'

def test_fetch_empty_database(db_connection: psycopg.Connection) -> None:
    """Fetching from an empty database should return empty list"""
    result = fetch_aggregated_product_scores(db_connection, category="Any", time_window="all_time")
    
    assert len(result) == 0
    assert result == []

def test_category_input_case_insensitive(db_connection: psycopg.Connection, single_sentiment_comment: dict[str, Any]) -> None:
    """category param should work for mixed casing"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO product_sentiment (
                comment_id, product_name, category, sentiment_score, created_utc
            ) VALUES (
                %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
            )
        """, single_sentiment_comment)

    result = fetch_aggregated_product_scores(db_connection, category="gPu", time_window="all_time")

    assert len(result) == 1
    assert result[0].product_name == 'rtx 4090'
    assert result[0].avg_sentiment == 0.89
    assert result[0].mention_count == 1
    assert result[0].positive_count == 1
    assert result[0].negative_count == 0
    assert result[0].neutral_count == 0
    assert result[0].approval_percentage == 100

def test_category_input_white_space(db_connection: psycopg.Connection, single_sentiment_comment: dict[str, Any]) -> None:
    """Category param should work with white space"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO product_sentiment (
                comment_id, product_name, category, sentiment_score, created_utc
            ) VALUES (
                %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
            )
        """, single_sentiment_comment)

    result = fetch_aggregated_product_scores(db_connection, category="  GPU  ", time_window="all_time")

    assert len(result) == 1
    assert result[0].product_name == 'rtx 4090'
    assert result[0].avg_sentiment == 0.89
    assert result[0].mention_count == 1
    assert result[0].positive_count == 1
    assert result[0].negative_count == 0
    assert result[0].neutral_count == 0
    assert result[0].approval_percentage == 100

def test_time_window_input_case_insensitive(db_connection: psycopg.Connection, single_sentiment_comment: dict[str, Any]) -> None:
    """time_window param should work for mixed casing"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO product_sentiment (
                comment_id, product_name, category, sentiment_score, created_utc
            ) VALUES (
                %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
            )
        """, single_sentiment_comment)

    result = fetch_aggregated_product_scores(db_connection, category="GPU", time_window="alL_tImE")

    assert len(result) == 1
    assert result[0].product_name == 'rtx 4090'
    assert result[0].avg_sentiment == 0.89
    assert result[0].mention_count == 1
    assert result[0].positive_count == 1
    assert result[0].negative_count == 0
    assert result[0].neutral_count == 0
    assert result[0].approval_percentage == 100

def test_time_window_input_white_space(db_connection: psycopg.Connection, single_sentiment_comment: dict[str, Any]) -> None:
    """time_window param should work with white space"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO product_sentiment (
                comment_id, product_name, category, sentiment_score, created_utc
            ) VALUES (
                %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
            )
        """, single_sentiment_comment)

    result = fetch_aggregated_product_scores(db_connection, category="GPU", time_window="  all_time  ")

    assert len(result) == 1
    assert result[0].product_name == 'rtx 4090'
    assert result[0].avg_sentiment == 0.89
    assert result[0].mention_count == 1
    assert result[0].positive_count == 1
    assert result[0].negative_count == 0
    assert result[0].neutral_count == 0
    assert result[0].approval_percentage == 100

def test_avg_aggregation_works_for_multiple_same_products(db_connection: psycopg.Connection) -> None:
    comments = [
        {
            'comment_id': 'test_comment_1',
            'product_name': 'rtx 4090',
            'category': 'GPU',
            'sentiment_score': 0.20,
            'created_utc': datetime.now()
        },
        {
            'comment_id': 'test_comment_2',
            'product_name': 'rtx 4090',
            'category': 'GPU',
            'sentiment_score': 0.60,
            'created_utc': datetime.now()
        },
        {
            'comment_id': 'test_comment_3',
            'product_name': 'rtx 4090',
            'category': 'GPU',
            'sentiment_score': 0.70,
            'created_utc': datetime.now()
        }
    ]

    with db_connection.cursor() as cursor:
        for comment in comments:
            cursor.execute("""
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """, comment)
        
    result = fetch_aggregated_product_scores(db_connection, category="GPU", time_window="all_time")

    assert len(result) == 1
    assert result[0].product_name == 'rtx 4090'
    assert result[0].avg_sentiment == 0.5

def test_sentiment_boundary_values(db_connection: psycopg.Connection) -> None:
    """Boundary threshold values for positive, neutral, negative should work"""
    comments = [
        {
            'comment_id': 'test_comment_1',
            'product_name': 'rtx 4070',
            'category': 'GPU',
            'sentiment_score': 0.20,
            'created_utc': datetime.now()
        },
        {
            'comment_id': 'test_comment_2',
            'product_name': 'rtx 4080',
            'category': 'GPU',
            'sentiment_score': 0.21,
            'created_utc': datetime.now()
        },
        {
            'comment_id': 'test_comment_3',
            'product_name': 'rtx 4090',
            'category': 'GPU',
            'sentiment_score': -0.20,
            'created_utc': datetime.now()
        },
        {
            'comment_id': 'test_comment_4',
            'product_name': 'rtx 5070',
            'category': 'GPU',
            'sentiment_score': -0.21,
            'created_utc': datetime.now()
        }
    ]

    with db_connection.cursor() as cursor:
        for comment in comments:
            cursor.execute("""
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """, comment)
        
    result = fetch_aggregated_product_scores(db_connection, category="GPU", time_window="all_time")

    assert len(result) == 4
    assert result[0].product_name == 'rtx 4080'
    assert result[0].positive_count

    assert result[1].product_name == 'rtx 4070'
    assert result[1].neutral_count
    assert not result[1].positive_count
    
    assert result[2].product_name == 'rtx 4090'
    assert result[2].neutral_count
    assert not result[2].negative_count

    assert result[3].product_name == 'rtx 5070'
    assert result[3].negative_count

def test_multiple_categories_in_database(db_connection: psycopg.Connection) -> None:
    """It should only fetch the product comments for the category specified"""
    comments = [
        {
            'comment_id': 'test_comment_1',
            'product_name': 'rtx 4090',
            'category': 'GPU',
            'sentiment_score': 0.20,
            'created_utc': datetime.now()
        },
        {
            'comment_id': 'test_comment_2',
            'product_name': 'dog',
            'category': 'Animals',
            'sentiment_score': 0.21,
            'created_utc': datetime.now()
        }
    ]

    with db_connection.cursor() as cursor:
        for comment in comments:
            cursor.execute("""
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """, comment)
        
    result = fetch_aggregated_product_scores(db_connection, category="GPU", time_window="all_time")

    assert len(result) == 1
    assert result[0].product_name == 'rtx 4090'

def test_empty_category_string(db_connection: psycopg.Connection) -> None:
    """Empty category string should return an empty list"""
    result = fetch_aggregated_product_scores(db_connection, category="", time_window="all_time")

    assert len(result) == 0
    assert result == []

def test_fetch_nonexistant_category(db_connection: psycopg.Connection, single_sentiment_comment: dict[str, Any]) -> None:
    """Trying to fetch comments for a category that doesnt exist should return empty list"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO product_sentiment (
                comment_id, product_name, category, sentiment_score, created_utc
            ) VALUES (
                %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
            )
        """, single_sentiment_comment)
        
    result = fetch_aggregated_product_scores(db_connection, category="dog", time_window="all_time")

    assert len(result) == 0
    assert result == []

def test_empty_time_window_string(db_connection: psycopg.Connection) -> None:
    """Empty category string should return an empty list"""
    result = fetch_aggregated_product_scores(db_connection, category="GPU", time_window="")

    assert len(result) == 0
    assert result == []

def boundary_date_for_time_window(db_connection: psycopg.Connection) -> None:
    """Boundary date (exactly 90d for 90d) should still be returned"""
    comment = {
        'comment_id': 'test_comment_1',
        'product_name': 'rtx 4090',
        'category': 'GPU',
        'sentiment_score': 0.20,
        'created_utc': datetime.now() - timedelta(days=90)
    }

    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO product_sentiment (
                comment_id, product_name, category, sentiment_score, created_utc
            ) VALUES (
                %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
            )
        """, comment)

    result = fetch_aggregated_product_scores(db_connection, category="GPU", time_window="90d")

    assert len(result) == 1
    assert result[0].product_name == 'rtx 4090'