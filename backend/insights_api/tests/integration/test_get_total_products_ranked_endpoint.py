from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.types.fastapi import FastAPITestClient
import pytest


@pytest.mark.asyncio
async def test_fetch_products_in_same_topic(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None,
) -> None:
    """Should fetch the count of products in same topic"""
    products = [
        {
            **single_product_ranking_row,
            "product_name": "product_gpu",
            "product_topic": "GPU",
        },
        {
            **single_product_ranking_row,
            "product_name": "product_cpu",
            "product_topic": "GPU",
        },
        {
            **single_product_ranking_row,
            "product_name": "product_photography",
            "product_topic": "tripod",
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

    response = await fastapi_client.client.get(
        "/api/v1/topic/total_products_ranked?product_topic=GPU"
    )

    assert response.status_code == 200
    assert response.json() == 2


@pytest.mark.asyncio
async def test_no_matching_products(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None,
) -> None:
    """If no products match the input category, it should return 0"""
    products = [
        {
            **single_product_ranking_row,
            "product_name": "product_gpu",
            "product_topic": "GPU",
        },
        {
            **single_product_ranking_row,
            "product_name": "product_cpu",
            "product_topic": "GPU",
        },
        {
            **single_product_ranking_row,
            "product_name": "product_photography",
            "product_topic": "tripod",
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

    response = await fastapi_client.client.get(
        "/api/v1/topic/total_products_ranked?product_topic=NONEXISTANT"
    )

    assert response.status_code == 200
    assert response.json() == 0
