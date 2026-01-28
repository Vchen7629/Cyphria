from datetime import timedelta
from datetime import timezone
from datetime import datetime
from typing import Any
from src.db.queries import fetch_unique_products
import psycopg


def test_fetch_single_product(
    db_connection: psycopg.Connection, single_product_sentiment: dict[str, Any]
) -> None:
    """Fetching a single comment from the database should return a list of a single product sentiment"""
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO product_sentiment (
                comment_id, product_name, category, sentiment_score, created_utc
            ) VALUES (
                %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
            )
        """,
            single_product_sentiment,
        )

    result = fetch_unique_products(db_connection, time_window="all_time", min_comments=1)

    assert len(result) == 1
    assert result == ["rtx 4090"]


def test_fetch_product_with_less_than_min_comments(
    db_connection: psycopg.Connection, single_product_sentiment: dict[str, Any]
) -> None:
    """When min comments is 10, fetching a product with 1 comment shouldnt return"""
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO product_sentiment (
                comment_id, product_name, category, sentiment_score, created_utc
            ) VALUES (
                %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
            )
        """,
            single_product_sentiment,
        )

    result = fetch_unique_products(db_connection, time_window="all_time", min_comments=10)

    assert len(result) == 0
    assert result == []


def test_fetch_empty_database(db_connection: psycopg.Connection) -> None:
    """Fetching from an empty database should return empty list"""
    result = fetch_unique_products(db_connection, time_window="all_time", min_comments=10)

    assert len(result) == 0
    assert result == []


def test_fetch_orders_by_comment_count_desc(
    db_connection: psycopg.Connection, single_product_sentiment: dict[str, Any]
) -> None:
    """Products with more comments should appear first"""
    products_with_counts = [("rtx 5090", 15), ("rtx 5080", 11)]

    product_sentiments = [
        {**single_product_sentiment, "product_name": name, "comment_id": f"test_comment_{name}_{i}"}
        for name, count in products_with_counts
        for i in range(1, count + 1)
    ]

    for i in range(len(product_sentiments)):
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """,
                product_sentiments[i],
            )

    result = fetch_unique_products(db_connection, time_window="all_time", min_comments=10)

    assert len(result) == 2
    assert result == ["rtx 5090", "rtx 5080"]


def test_fetch_only_last_90_day(
    db_connection: psycopg.Connection, single_product_sentiment: dict[str, Any]
) -> None:
    """90 day time_window should fetch only products that have comments from last 90 days"""
    products_with_counts = [
        (
            "rtx 5090",
            datetime.now(timezone.utc) - timedelta(days=5),
            11,
        ),  # rtx 5090 is valid since its only 5 days old
        (
            "rtx 5080",
            datetime.now(timezone.utc) - timedelta(days=300),
            16,
        ),  # rtx 5080 is invalid since its 300 days old
    ]

    product_sentiments = [
        {
            **single_product_sentiment,
            "product_name": name,
            "created_utc": created_utc,
            "comment_id": f"test_comment_{name}_{i}",
        }
        for name, created_utc, count in products_with_counts
        for i in range(1, count + 1)
    ]

    for i in range(len(product_sentiments)):
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """,
                product_sentiments[i],
            )

    result = fetch_unique_products(db_connection, time_window="90d", min_comments=10)

    assert len(result) == 1
    assert result == ["rtx 5090"]


def test_time_window_90_day_border(
    db_connection: psycopg.Connection, single_product_sentiment: dict[str, Any]
) -> None:
    """Products that are exactly 90 days old (using 89 days ) should still be fetched"""
    products_with_counts = [
        (
            "rtx 5090",
            datetime.now(timezone.utc) - timedelta(days=5),
            11,
        ),  # rtx 5090 is valid since its only 5 days old
        # rtx 5080 is also valid since its exactly 90 days old, using 89 days, 23 hours, 59 minutes, ... since there is small delay
        # between insert and fetch
        (
            "rtx 5080",
            datetime.now(timezone.utc)
            - timedelta(days=89, hours=23, minutes=59, seconds=59, milliseconds=999),
            16,
        ),
    ]

    product_sentiments = [
        {
            **single_product_sentiment,
            "product_name": name,
            "created_utc": created_utc,
            "comment_id": f"test_comment_{name}_{i}",
        }
        for name, created_utc, count in products_with_counts
        for i in range(1, count + 1)
    ]

    for i in range(len(product_sentiments)):
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO product_sentiment (
                    comment_id, product_name, category, sentiment_score, created_utc
                ) VALUES (
                    %(comment_id)s, %(product_name)s, %(category)s, %(sentiment_score)s, %(created_utc)s
                )
            """,
                product_sentiments[i],
            )

    result = fetch_unique_products(db_connection, time_window="90d", min_comments=10)

    assert len(result) == 2
    assert result == ["rtx 5080", "rtx 5090"]
