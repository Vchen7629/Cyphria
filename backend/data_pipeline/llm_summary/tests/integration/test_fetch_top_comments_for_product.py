from datetime import timedelta
from datetime import timezone
from datetime import datetime
from typing import Any
from src.db.queries import fetch_top_comments_for_product
import psycopg


def test_fetch_single_product_comments(
    db_connection: psycopg.Connection,
    single_raw_comment: dict[str, Any],
    single_product_sentiment: dict[str, Any],
) -> None:
    """Fetching a single comment from the database should return a list of the product comments"""
    product_comments = [
        ("rtx 4090 comment 1", ["rtx 4090"]),
        ("rtx 4090 comment 2", ["rtx 4090"]),
        ("rtx 4090 comment 3", ["rtx 4090"]),
        ("rtx 4090 comment 4", ["rtx 4090"]),
        ("rtx 4090 comment 5", ["rtx 4090"]),
    ]

    raw_comments = [
        {
            **single_raw_comment,
            "comment_id": f"comment_{i}",
            "comment_body": comment_body,
            "detected_products": detected_products,
        }
        for i, (comment_body, detected_products) in enumerate(product_comments)
    ]

    for raw_comment in raw_comments:
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO raw_comments (
                    comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, category
                ) VALUES (
                    %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s,
                    %(subreddit)s, %(author)s, %(score)s, %(created_utc)s, %(category)s
                )
            """,
                raw_comment,
            )

    sentiments = [0.23, 0.89, 0.57, 0.33, 0.49]

    product_sentiments = [
        {**single_product_sentiment, "comment_id": f"comment_{i}", "sentiment_score": product_score}
        for i, product_score in enumerate(sentiments)
    ]

    for product_sentiment in product_sentiments:
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """,
                product_sentiment,
            )

    result = fetch_top_comments_for_product(
        db_connection, product_name="rtx 4090", time_window="all_time"
    )

    assert len(result) == 5
    assert result == [
        "rtx 4090 comment 1",
        "rtx 4090 comment 2",
        "rtx 4090 comment 3",
        "rtx 4090 comment 4",
        "rtx 4090 comment 5",
    ]


def test_fetches_ordered_positive_negative_neutral_comments(
    db_connection: psycopg.Connection,
    single_raw_comment: dict[str, Any],
    single_product_sentiment: dict[str, Any],
) -> None:
    """Query should return the list with first 10 comments positive, 10 comments negative, last 5 negative"""
    product_comments = [(f"rtx 4090 comment {i}", ["rtx 4090"]) for i in range(1, 26)]

    raw_comments = [
        {
            **single_raw_comment,
            "comment_id": f"comment_{i}",
            "comment_body": comment_body,
            "detected_products": detected_products,
        }
        for i, (comment_body, detected_products) in enumerate(product_comments)
    ]

    for raw_comment in raw_comments:
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO raw_comments (
                    comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, category
                ) VALUES (
                    %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s,
                    %(subreddit)s, %(author)s, %(score)s, %(created_utc)s, %(category)s
                )
            """,
                raw_comment,
            )

    sentiments = [
        0.1,
        0.15,
        0.11,
        -0.1,  # neutral scores
        0.11,
        0.9,
        0.23,
        0.33,
        0.54,
        0.45,
        0.77,
        0.71,
        0.99,
        0.95,
        0.70,  # positive scores
        -0.99,
        -0.33,
        -0.55,
        -0.44,
        -0.72,
        -0.59,
        -0.23,
        -0.34,
        -0.77,
        -0.69,  # negative scores
    ]

    product_sentiments = [
        {**single_product_sentiment, "comment_id": f"comment_{i}", "sentiment_score": product_score}
        for i, product_score in enumerate(sentiments)
    ]

    for product_sentiment in product_sentiments:
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """,
                product_sentiment,
            )

    result = fetch_top_comments_for_product(
        db_connection, product_name="rtx 4090", time_window="all_time"
    )

    assert len(result) == 25
    assert "rtx 4090 comment 6" in result[:10]  # positive comment should be in the first 10 values
    assert "rtx 4090 comment 24" in result[10:20]  # negative comment should be in next 10 values
    assert "rtx 4090 comment 1" in result[20:25]  # neutral in last 5


def test_fetch_only_last_90_day(
    db_connection: psycopg.Connection,
    single_raw_comment: dict[str, Any],
    single_product_sentiment: dict[str, Any],
) -> None:
    """90 day time_window should fetch only products that have comments from last 90 days"""
    product_comments = [
        (
            f"rtx 4090 comment {i}",
            ["rtx 4090"],
            datetime.now(timezone.utc) - timedelta(days=5 if i < 7 else 300),
        )
        for i in range(18)
    ]

    raw_comments = [
        {
            **single_raw_comment,
            "comment_id": f"comment_{i}",
            "comment_body": comment_body,
            "detected_products": detected_products,
            "created_utc": created_utc,
        }
        for i, (comment_body, detected_products, created_utc) in enumerate(product_comments)
    ]

    for raw_comment in raw_comments:
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO raw_comments (
                    comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, category
                ) VALUES (
                    %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s,
                    %(subreddit)s, %(author)s, %(score)s, %(created_utc)s, %(category)s
                )
            """,
                raw_comment,
            )

    product_sentiments = [
        {**single_product_sentiment, "comment_id": f"comment_{i}"} for i in range(len(raw_comments))
    ]

    for product_sentiment in product_sentiments:
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """,
                product_sentiment,
            )

    result = fetch_top_comments_for_product(
        db_connection, product_name="rtx 4090", time_window="90d"
    )

    assert len(result) == 7
    assert "rtx 4090 comment 8" not in result


def test_90_day_boundary(
    db_connection: psycopg.Connection,
    single_raw_comment: dict[str, Any],
    single_product_sentiment: dict[str, Any],
) -> None:
    """Posts that are exactly 90 days old should be fetched but products older shouldnt"""
    product_comments = [
        (
            f"rtx 4090 comment {i}",
            ["rtx 4090"],
            datetime.now(timezone.utc)
            - timedelta(days=89, hours=23, minutes=59, seconds=59, milliseconds=999)
            if i < 7
            else datetime.now(timezone.utc) - timedelta(days=90, seconds=1),
        )
        for i in range(18)
    ]

    raw_comments = [
        {
            **single_raw_comment,
            "comment_id": f"comment_{i}",
            "comment_body": comment_body,
            "detected_products": detected_products,
            "created_utc": created_utc,
        }
        for i, (comment_body, detected_products, created_utc) in enumerate(product_comments)
    ]

    for raw_comment in raw_comments:
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO raw_comments (
                    comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, category
                ) VALUES (
                    %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s,
                    %(subreddit)s, %(author)s, %(score)s, %(created_utc)s, %(category)s
                )
            """,
                raw_comment,
            )

    product_sentiments = [
        {**single_product_sentiment, "comment_id": f"comment_{i}"} for i in range(len(raw_comments))
    ]

    for product_sentiment in product_sentiments:
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """,
                product_sentiment,
            )

    result = fetch_top_comments_for_product(
        db_connection, product_name="rtx 4090", time_window="90d"
    )

    assert len(result) == 7
    assert "rtx 4090 comment 8" not in result


def test_fetch_empty_database(db_connection: psycopg.Connection) -> None:
    """Fetching from an empty database should return empty list"""
    result = fetch_top_comments_for_product(
        db_connection, product_name="idk", time_window="all_time"
    )

    assert len(result) == 0
    assert result == []
