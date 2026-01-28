from typing import Any
from datetime import datetime
from datetime import timezone
from src.db_utils.queries import mark_comments_processed
import psycopg


def test_mark_single_comment_processed(
    db_connection: psycopg.Connection, single_comment: dict[str, Any]
) -> None:
    """Marking a valid comment id should work."""
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, FALSE
            )
        """,
            single_comment,
        )

    db_connection.commit()

    updated_rows = mark_comments_processed(db_connection, ["test_comment_1"])

    assert updated_rows == 1

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT sentiment_processed \
            FROM raw_comments \
            WHERE comment_id = %s;",
            ("test_comment_1",),
        )

        result = cursor.fetchone()
        assert result is not None
        assert result[0]


def test_mark_already_processed_comment(
    db_connection: psycopg.Connection, single_comment: dict[str, Any]
) -> None:
    """Marking a already processed comment shouldnt update the database."""
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, TRUE
            )
        """,
            single_comment,
        )

    db_connection.commit()

    updated_rows = mark_comments_processed(db_connection, ["test_comment_1"])

    assert updated_rows == 0

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT sentiment_processed \
            FROM raw_comments \
            WHERE comment_id = %s;",
            ("test_comment_1",),
        )

        result = cursor.fetchone()
        assert result is not None
        assert result[0]


def test_mark_non_existant_comment(
    db_connection: psycopg.Connection, single_comment: dict[str, Any]
) -> None:
    """Marking a non existant comment shouldnt update the database."""
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, FALSE
            )
        """,
            single_comment,
        )

    db_connection.commit()

    updated_rows = mark_comments_processed(db_connection, ["non existant id"])

    assert updated_rows == 0

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT sentiment_processed \
            FROM raw_comments \
            WHERE comment_id = %s;",
            ("test_comment_1",),
        )

        result = cursor.fetchone()
        assert result is not None
        assert not result[0]


def test_mark_comment_in_empty_database(db_connection: psycopg.Connection) -> None:
    """Marking a comment in an empty database shouldnt update anything"""
    assert mark_comments_processed(db_connection, comment_ids=["idk"]) == 0


def test_mark_existing_non_existing_comment(db_connection: psycopg.Connection) -> None:
    """
    Only existing comment ids should be updated when we have a
    mix of existing and non-existing comment ids
    """
    comments = [
        {
            "comment_id": "existing_1",
            "created_utc": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        },
        {
            "comment_id": "existing_2",
            "created_utc": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        },
        {
            "comment_id": "existing_3",
            "created_utc": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        },
    ]

    with db_connection.cursor() as cursor:
        for i, comment in enumerate(comments):
            cursor.execute(
                """                                                                        
                INSERT INTO raw_comments (                                                            
                    comment_id, post_id, comment_body, detected_products,                             
                    subreddit, author, score, created_utc, product_topic, sentiment_processed              
                ) VALUES (                                                                            
                    %(comment_id)s, 'post', 'body', ARRAY['product'],                                 
                    'sub', 'author', 1, %(created_utc)s, 'cat', FALSE               
                )                                                                                     
            """,
                {"comment_id": comment["comment_id"], "created_utc": comment["created_utc"]},
            )

    updated_row = mark_comments_processed(
        db_connection, ["existing_1", "existing_2", "nonexisting_id"]
    )

    assert updated_row == 2

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT sentiment_processed \
            FROM raw_comments \
            WHERE comment_id = %s;",
            ("existing_1",),
        )

        result = cursor.fetchone()
        assert result is not None
        assert result[0]

        cursor.execute(
            "SELECT sentiment_processed \
            FROM raw_comments \
            WHERE comment_id = %s;",
            ("existing_3",),
        )

        result = cursor.fetchone()
        assert result is not None
        assert not result[0]


def test_empty_comment_input_list(db_connection: psycopg.Connection) -> None:
    """Empty comment id input list should return 0"""
    assert mark_comments_processed(db_connection, []) == 0


def test_duplicate_comment_ids_in_input_list(db_connection: psycopg.Connection) -> None:
    """Duplicate comment ids should only update the unique amount"""
    comments = [
        {
            "comment_id": "existing_1",
            "created_utc": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        },
        {
            "comment_id": "existing_2",
            "created_utc": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        },
    ]

    with db_connection.cursor() as cursor:
        for i, comment in enumerate(comments):
            cursor.execute(
                """                                                                        
                INSERT INTO raw_comments (                                                            
                    comment_id, post_id, comment_body, detected_products,                             
                    subreddit, author, score, created_utc, product_topic, sentiment_processed              
                ) VALUES (                                                                            
                    %(comment_id)s, 'post', 'body', ARRAY['product'],                                 
                    'sub', 'author', 1, %(created_utc)s, 'cat', FALSE               
                )                                                                                     
            """,
                {"comment_id": comment["comment_id"], "created_utc": comment["created_utc"]},
            )

    updated_rows = mark_comments_processed(
        db_connection, ["existing_1", "existing_1", "existing_2", "existing_2"]
    )

    assert updated_rows == 2

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT sentiment_processed \
            FROM raw_comments \
            WHERE comment_id = %s;",
            ("existing_1",),
        )

        result = cursor.fetchone()
        assert result is not None
        assert result[0]

        cursor.execute(
            "SELECT sentiment_processed \
            FROM raw_comments \
            WHERE comment_id = %s;",
            ("existing_2",),
        )

        result = cursor.fetchone()
        assert result is not None
        assert result[0]


def test_special_characters_in_comment_ids(db_connection: psycopg.Connection) -> None:
    """Comment IDs with special chars (quotes, backslashes, Unicode, etc) should match"""
    special_ids = [
        "comment'with'quotes",
        'comment"with"double',
        "comment\\with\\backslash",
        "comment;DROP TABLE--",
        "comment_with_émojis_ünïcödé",
    ]

    with db_connection.cursor() as cursor:
        for comment_id in special_ids:
            cursor.execute(
                """
                INSERT INTO raw_comments (
                    comment_id, post_id, comment_body, detected_products,
                    subreddit, author, score, created_utc, product_topic, sentiment_processed
                ) VALUES (
                    %s, 'post', 'body', ARRAY['product'],
                    'sub', 'author', 1, %s, 'cat', FALSE
                )
            """,
                (comment_id, datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
            )

    db_connection.commit()

    updated_rows = mark_comments_processed(db_connection, special_ids)

    assert updated_rows == 5

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT sentiment_processed \
            FROM raw_comments \
            WHERE comment_id = %s;",
            ("""comment'with'quotes""",),
        )

        result = cursor.fetchone()
        assert result is not None
        assert result[0]

        cursor.execute(
            "SELECT sentiment_processed \
            FROM raw_comments \
            WHERE comment_id = %s;",
            ("""comment\\with\\backslash""",),
        )

        result = cursor.fetchone()
        assert result is not None
        assert result[0]

        cursor.execute(
            "SELECT sentiment_processed \
            FROM raw_comments \
            WHERE comment_id = %s;",
            ("""comment;DROP TABLE--""",),
        )

        result = cursor.fetchone()
        assert result is not None
        assert result[0]
