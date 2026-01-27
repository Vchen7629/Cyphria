from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.types.fastapi import FastAPITestClient
import pytest


@pytest.mark.asyncio
async def test_non_existing_product_name(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None,
) -> None:
    """Searching for a product name that doesnt match should return empty array"""
    async with test_async_session() as session:
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
            single_product_ranking_row,
        )
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/product/sentiment_scores?product_name=auuugh&time_window=all_time"
    )

    assert response.status_code == 404
    data = response.json()
    assert (
        data["detail"]
        == "Sentiment counts not found for product: auuugh time_window: all_time"
    )


@pytest.mark.parametrize(argnames="time_window", argvalues=["90d", "all_time"])
@pytest.mark.asyncio
async def test_correct_time_window(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    time_window: str,
    clean_tables: None,
) -> None:
    """Product on the boundary of 90 days should be fetched"""
    products = [
        {
            **single_product_ranking_row,
            "product_name": "product_1",
            "positive_count": 50,
            "time_window": "90d",
        },
        {
            **single_product_ranking_row,
            "product_name": "product_1",
            "positive_count": 55,
            "time_window": "all_time",
        },
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

    product_res = await fastapi_client.client.get(
        f"/api/v1/product/sentiment_scores?product_name=product_1&time_window={time_window}"
    )

    assert product_res.status_code == 200
    product_data = product_res.json()
    products = product_data["product"]

    if time_window == "90d":
        assert products["positive_sentiment_count"] == 50
    else:
        assert products["positive_sentiment_count"] == 55
