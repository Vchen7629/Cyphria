from typing import Any
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.types.fastapi import FastAPITestClient
import pytest


@pytest.mark.asyncio
async def test_counts_only_matching_topic(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_raw_comment: dict[str, Any],
    clean_tables: None,
) -> None:
    """It should only count comments that are matching the topic"""
    comments = [
        {
            **single_raw_comment,
            "comment_id": "comment_1",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=30),
        },
        {
            **single_raw_comment,
            "comment_id": "comment_2",
            "product_topic": "CPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=60),
        },
        {
            **single_raw_comment,
            "comment_id": "comment_3",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=91),
        },
        {
            **single_raw_comment,
            "comment_id": "comment_4",
            "product_topic": "CPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=120),
        },
        {
            **single_raw_comment,
            "comment_id": "comment_5",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=5),
        },
    ]

    async with test_async_session() as session:
        for comment in comments:
            await session.execute(
                text("""
                INSERT INTO raw_comments
                    (comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed)
                VALUES
                    (:comment_id, :post_id, :comment_body, :detected_products, :subreddit,
                    :author, :score, :created_utc, :product_topic, :sentiment_processed)
            """),
                comment,
            )
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/topic/total_comments?product_topic=GPU&time_window=all_time"
    )

    assert response.status_code == 200
    assert response.json() == 3


@pytest.mark.asyncio
async def test_time_window_all_time(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_raw_comment: dict[str, Any],
    clean_tables: None,
) -> None:
    """top_comments endpoint with all_time should include older comments."""
    comments = [
        {
            **single_raw_comment,
            "comment_id": f"comment_{i}",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=89 + i),
        }
        for i in range(5)
    ]

    async with test_async_session() as session:
        for comment in comments:
            await session.execute(
                text("""
                INSERT INTO raw_comments
                    (comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed)
                VALUES
                    (:comment_id, :post_id, :comment_body, :detected_products, :subreddit,
                    :author, :score, :created_utc, :product_topic, :sentiment_processed)
            """),
                comment,
            )
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/topic/total_comments?product_topic=GPU&time_window=all_time"
    )

    assert response.status_code == 200
    assert response.json() == 5


@pytest.mark.asyncio
async def test_time_window_90_day(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_raw_comment: dict[str, Any],
    clean_tables: None,
) -> None:
    """top_comments endpoint should return comments with 90 day time window ordered by score."""
    comments = [
        {
            **single_raw_comment,
            "comment_id": "comment_1",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=30),
        },
        {
            **single_raw_comment,
            "comment_id": "comment_2",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=60),
        },
        {
            **single_raw_comment,
            "comment_id": "comment_3",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=91),
        },
        {
            **single_raw_comment,
            "comment_id": "comment_4",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=120),
        },
        {
            **single_raw_comment,
            "comment_id": "comment_5",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=5),
        },
    ]
    async with test_async_session() as session:
        for comment in comments:
            await session.execute(
                text("""
                INSERT INTO raw_comments
                    (comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed)
                VALUES
                    (:comment_id, :post_id, :comment_body, :detected_products, :subreddit,
                    :author, :score, :created_utc, :product_topic, :sentiment_processed)
            """),
                comment,
            )
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/topic/total_comments?product_topic=GPU&time_window=90d"
    )

    assert response.status_code == 200
    assert response.json() == 3


@pytest.mark.asyncio
async def test_time_window_90_day_boundary(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_raw_comment: dict[str, Any],
    clean_tables: None,
) -> None:
    """top_comments should include comments within 90 days but exclude older."""
    comments = [
        {
            **single_raw_comment,
            "comment_id": "comment_1",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=89),
        },
        {
            **single_raw_comment,
            "comment_id": "comment_2",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc)
            - timedelta(days=89, hours=23, minutes=59, seconds=59),
        },
        {
            **single_raw_comment,
            "comment_id": "comment_3",
            "product_topic": "GPU",
            "created_utc": datetime.now(tz=timezone.utc)
            - timedelta(days=90, milliseconds=999),
        },
    ]

    async with test_async_session() as session:
        for comment in comments:
            await session.execute(
                text("""
                INSERT INTO raw_comments
                    (comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed)
                VALUES
                    (:comment_id, :post_id, :comment_body, :detected_products, :subreddit,
                    :author, :score, :created_utc, :product_topic, :sentiment_processed)
            """),
                comment,
            )
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/topic/total_comments?product_topic=GPU&time_window=90d"
    )

    assert response.status_code == 200
    assert response.json() == 2
