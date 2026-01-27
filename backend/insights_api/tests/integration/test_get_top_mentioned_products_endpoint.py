from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.types.fastapi import FastAPITestClient
import pytest


@pytest.mark.asyncio
async def test_fetch_top_6_products(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None,
) -> None:
    """Should fetch the top 6 most mentioned products"""
    products = [
        {
            **single_product_ranking_row,
            "product_name": f"product_{i}",
            "mention_count": 100 * (i + 1),
        }
        for i in range(12)
    ]

    async with test_async_session() as session:
        for product in products:
            await session.execute(
                text("""
                INSERT INTO product_rankings
                    (product_name, product_topic, time_window, rank, grade, bayesian_score,
                    avg_sentiment, mention_count, approval_percentage, positive_count, neutral_count,
                    negative_count, is_top_pick, is_most_discussed, has_limited_data, calculation_date)
                VALUES
                    (:product_name, :product_topic, :time_window, :rank, :grade, :bayesian_score,
                    :avg_sentiment, :mention_count, :approval_percentage, :positive_count, :neutral_count,
                    :negative_count, :is_top_pick, :is_most_discussed, :has_limited_data, :calculation_date)
                """),
                product,
            )
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/category/top_mentioned_products?category=Computing"
    )

    assert response.status_code == 200
    data = response.json()
    comments = data["products"]

    assert len(comments) == 6

    # Should be ordered by score descending
    assert comments[0]["product_name"] == "product_11"
    assert comments[1]["product_name"] == "product_10"
    assert comments[2]["product_name"] == "product_9"
    assert comments[3]["product_name"] == "product_8"
    assert comments[4]["product_name"] == "product_7"
    assert comments[5]["product_name"] == "product_6"


@pytest.mark.asyncio
async def test_identical_mention_count(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None,
) -> None:
    """Products with duplicate mention count should be handled"""
    products = [
        {
            **single_product_ranking_row,
            "product_name": f"product_{i}",
            "mention_count": 100,
        }
        for i in range(3)
    ]

    async with test_async_session() as session:
        for product in products:
            await session.execute(
                text("""
                INSERT INTO product_rankings
                    (product_name, product_topic, time_window, rank, grade, bayesian_score,
                    avg_sentiment, mention_count, approval_percentage, positive_count, neutral_count,
                    negative_count, is_top_pick, is_most_discussed, has_limited_data, calculation_date)
                VALUES
                    (:product_name, :product_topic, :time_window, :rank, :grade, :bayesian_score,
                    :avg_sentiment, :mention_count, :approval_percentage, :positive_count, :neutral_count,
                    :negative_count, :is_top_pick, :is_most_discussed, :has_limited_data, :calculation_date)
                """),
                product,
            )
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/category/top_mentioned_products?category=Computing"
    )

    assert response.status_code == 200
    data = response.json()
    comments = data["products"]

    assert len(comments) == 3

    assert comments[0]["product_name"] == "product_0"
    assert comments[1]["product_name"] == "product_1"
    assert comments[2]["product_name"] == "product_2"
