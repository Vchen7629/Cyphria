from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.types.fastapi import FastAPITestClient
import pytest

@pytest.mark.asyncio
async def test_fetch_products_in_same_category(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None
) -> None:
    """Should fetch the count of products in same category"""
    products = [
        {**single_product_ranking_row, "product_name": f"product_gpu", "product_topic": "GPU", "mention_count": 100},
        {**single_product_ranking_row, "product_name": f"product_cpu", "product_topic": "CPU", "mention_count": 70},
        {**single_product_ranking_row, "product_name": f"product_photography", "product_topic": "tripod", "mention_count": 22},
    ]

    async with test_async_session() as session:
        for product in products:
            await session.execute(text("""
                INSERT INTO product_rankings
                    (product_name, product_topic, time_window, rank, grade, bayesian_score,
                    avg_sentiment, mention_count, approval_percentage, positive_count, neutral_count,
                    negative_count, is_top_pick, is_most_discussed, has_limited_data, calculation_date)
                VALUES
                    (:product_name, :product_topic, :time_window, :rank, :grade, :bayesian_score,
                    :avg_sentiment, :mention_count, :approval_percentage, :positive_count, :neutral_count,
                    :negative_count, :is_top_pick, :is_most_discussed, :has_limited_data, :calculation_date)
                """), product)
        await session.commit()
    
    response = await fastapi_client.client.get("/api/v1/category/total_products_count?category=Computing")

    assert response.status_code == 200
    assert response.json() == 2

@pytest.mark.asyncio
async def test_no_matching_products(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None
) -> None:
    """If no products match the input category, it should return 0"""
    products = [
        {**single_product_ranking_row, "product_name": f"product_gpu", "product_topic": "GPU", "mention_count": 100},
        {**single_product_ranking_row, "product_name": f"product_cpu", "product_topic": "CPU", "mention_count": 70},
        {**single_product_ranking_row, "product_name": f"product_photography", "product_topic": "tripod", "mention_count": 22},
    ]

    async with test_async_session() as session:
        for product in products:
            await session.execute(text("""
                INSERT INTO product_rankings
                    (product_name, product_topic, time_window, rank, grade, bayesian_score,
                    avg_sentiment, mention_count, approval_percentage, positive_count, neutral_count,
                    negative_count, is_top_pick, is_most_discussed, has_limited_data, calculation_date)
                VALUES
                    (:product_name, :product_topic, :time_window, :rank, :grade, :bayesian_score,
                    :avg_sentiment, :mention_count, :approval_percentage, :positive_count, :neutral_count,
                    :negative_count, :is_top_pick, :is_most_discussed, :has_limited_data, :calculation_date)
                """), product)
        await session.commit()
    
    response = await fastapi_client.client.get("/api/v1/category/total_products_count?category=Mobile")

    assert response.status_code == 200
    assert response.json() == 0