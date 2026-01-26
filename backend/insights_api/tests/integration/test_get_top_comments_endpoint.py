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
async def test_time_window_90_day(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_raw_comment: dict[str, Any],
    clean_tables: None
) -> None:
    """top_comments endpoint should return comments with 90 day time window ordered by score."""
    comments = [
        {**single_raw_comment, "comment_id": "comment_1", "score": 150, "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=30)},
        {**single_raw_comment, "comment_id": "comment_2", "score": 100, "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=60)},
        {**single_raw_comment, "comment_id": "comment_3", "score": 75, "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=10)},
        {**single_raw_comment, "comment_id": "comment_4", "score": 200, "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=120)},
        {**single_raw_comment, "comment_id": "comment_5", "score": 50, "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=5)},
    ]
    async with test_async_session() as session:
        for comment in comments:
            await session.execute(text("""
                INSERT INTO raw_comments
                    (comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed)
                VALUES
                    (:comment_id, :post_id, :comment_body, :detected_products, :subreddit,
                    :author, :score, :created_utc, :product_topic, :sentiment_processed)
            """), comment)
        await session.commit()

    response = await fastapi_client.client.get("/api/v1/product/top_comments?product_name=nvidia rtx 4090&time_window=90d")

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    assert len(comments) == 4

    # Should be ordered by score descending
    assert comments[0]["score"] == 150
    assert comments[1]["score"] == 100
    assert comments[2]["score"] == 75
    assert comments[3]["score"] == 50

@pytest.mark.asyncio
async def test_time_window_all_time(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_raw_comment: dict[str, Any],
    clean_tables: None
) -> None:
    """top_comments endpoint with all_time should include older comments."""
    comments = [
        {**single_raw_comment, "comment_id": f"comment_{i}", "score": 100 + i, "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=89 + i)}
        for i in range(5)
    ]

    async with test_async_session() as session:
        for comment in comments:
            await session.execute(text("""
                INSERT INTO raw_comments
                    (comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed)
                VALUES
                    (:comment_id, :post_id, :comment_body, :detected_products, :subreddit,
                    :author, :score, :created_utc, :product_topic, :sentiment_processed)
            """), comment)
        await session.commit()

    response = await fastapi_client.client.get("/api/v1/product/top_comments?product_name=nvidia rtx 4090&time_window=all_time")

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    assert len(comments) == 5

    assert comments[0]["score"] == 104

@pytest.mark.asyncio
async def test_comments_all_unprocessed(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_raw_comment: dict[str, Any],
    clean_tables: None
) -> None:
    """top_comments should return return a 404 error when no comments that are processed match the name."""
    comments = [
        {**single_raw_comment, "comment_id": "comment_1", "sentiment_processed": False},
        {**single_raw_comment, "comment_id": "comment_2", "sentiment_processed": False}
    ]

    async with test_async_session() as session:
        for comment in comments:
            await session.execute(text("""
                INSERT INTO raw_comments
                    (comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed)
                VALUES
                    (:comment_id, :post_id, :comment_body, :detected_products, :subreddit,
                    :author, :score, :created_utc, :product_topic, :sentiment_processed)
            """), comment)
        await session.commit()

    response = await fastapi_client.client.get("/api/v1/product/top_comments?product_name=nvidia rtx 4090&time_window=90d")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No reddit comments found for product: nvidia rtx 4090 and time_window: 90d"

@pytest.mark.asyncio
async def test_comments_identical_scores(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_raw_comment: dict[str, Any],
    clean_tables: None
) -> None:
    """top_comments should handle comments with identical scores."""
    comments = [
        {**single_raw_comment, "comment_id": f"comment_{i}", "detected_products": ["rtx 4080"], "score": 100}
        for i in range(3)
    ]

    async with test_async_session() as session:
        for comment in comments:
            await session.execute(text("""
                INSERT INTO raw_comments
                    (comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed)
                VALUES
                    (:comment_id, :post_id, :comment_body, :detected_products, :subreddit,
                    :author, :score, :created_utc, :product_topic, :sentiment_processed)
            """), comment)
        await session.commit()

    response = await fastapi_client.client.get("/api/v1/product/top_comments?product_name=rtx 4080&time_window=all_time")

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    assert len(comments) == 3
    # All should have score 100
    assert all(c["score"] == 100 for c in comments)

@pytest.mark.asyncio
async def test_returns_only_5(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_raw_comment: dict[str, Any],
    clean_tables: None
) -> None:
    """top_comments should return only top 5 when there are more than 5 comments."""
    comments = [
        {**single_raw_comment, "comment_id": f"comment_{i}", "detected_products": ["rtx 4080"], "score": 100 * (i + 1)}
        for i in range(10)
    ]

    async with test_async_session() as session:
        for comment in comments:
            await session.execute(text("""
                INSERT INTO raw_comments
                    (comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed)
                VALUES
                    (:comment_id, :post_id, :comment_body, :detected_products, :subreddit,
                    :author, :score, :created_utc, :product_topic, :sentiment_processed)
            """), comment)
        await session.commit()

    response = await fastapi_client.client.get("/api/v1/product/top_comments?product_name=rtx 4080&time_window=all_time")

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    assert len(comments) == 5
    assert comments[0]["score"] == 1000
    assert comments[4]["score"] == 600
    scores = [c["score"] for c in comments]
    assert 400 not in scores
    assert 100 not in scores

@pytest.mark.asyncio
async def test_comments_negative_and_zero_scores(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_raw_comment: dict[str, Any],
    clean_tables: None
) -> None:
    """top_comments should include and correctly order negative and zero score comments."""
    comments = [
        {**single_raw_comment, "comment_id": "comment_1", "score": 50},
        {**single_raw_comment, "comment_id": "comment_2", "score": 0},
        {**single_raw_comment, "comment_id": "comment_3", "score": -10},
        {**single_raw_comment, "comment_id": "comment_4", "score": -50},
    ]

    async with test_async_session() as session:
        for comment in comments:
            await session.execute(text("""
                INSERT INTO raw_comments
                    (comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed)
                VALUES
                    (:comment_id, :post_id, :comment_body, :detected_products, :subreddit,
                    :author, :score, :created_utc, :product_topic, :sentiment_processed)
            """), comment)
        await session.commit()

    response = await fastapi_client.client.get("/api/v1/product/top_comments?product_name=nvidia rtx 4090&time_window=all_time")

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    assert len(comments) == 4
    assert comments[0]["score"] == 50
    assert comments[1]["score"] == 0
    assert comments[2]["score"] == -10
    assert comments[3]["score"] == -50


@pytest.mark.asyncio
async def test_time_window_90_day_boundary(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_raw_comment: dict[str, Any],
    clean_tables: None
) -> None:
    """top_comments should include comments within 90 days but exclude older."""
    comments = [
        {**single_raw_comment, "comment_id": "comment_1", "score": 50, "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=89)},
        {**single_raw_comment, "comment_id": "comment_2", "score": 0, "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=89, hours=23, minutes=59, seconds=59)},
        {**single_raw_comment, "comment_id": "comment_3", "score": -10, "created_utc": datetime.now(tz=timezone.utc) - timedelta(days=90, milliseconds=999)},
    ]

    async with test_async_session() as session:
        for comment in comments:
            await session.execute(text("""
                INSERT INTO raw_comments
                    (comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed)
                VALUES
                    (:comment_id, :post_id, :comment_body, :detected_products, :subreddit,
                    :author, :score, :created_utc, :product_topic, :sentiment_processed)
            """), comment)
        await session.commit()

    response = await fastapi_client.client.get("/api/v1/product/top_comments?product_name=nvidia rtx 4090&time_window=90d")

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    # Should include comments inside 90 days, exclude outside
    assert len(comments) == 2
    scores = [c["score"] for c in comments]
    assert 50 in scores
    assert 0 in scores
    assert -10 not in scores