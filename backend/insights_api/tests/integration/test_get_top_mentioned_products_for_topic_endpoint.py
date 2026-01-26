from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.types.fastapi import FastAPITestClient
import pytest

@pytest.mark.asyncio
async def test_fetch_top_3_products(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None
) -> None:
    """Should only fetch the top 3 products"""
    products = [
        {**single_product_ranking_row, "product_name": f"product_1", "mention_count": 100},
        {**single_product_ranking_row, "product_name": f"product_2", "mention_count": 70},
        {**single_product_ranking_row, "product_name": f"product_3", "mention_count": 22},
        {**single_product_ranking_row, "product_name": f"product_4", "mention_count": 999},
        {**single_product_ranking_row, "product_name": f"product_5", "mention_count": 200},
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
    
    response = await fastapi_client.client.get("/api/v1/category/topic_most_mentioned_product?product_topic=GPU")

    assert response.status_code == 200
    product_data = response.json()
    products = product_data["products"]

    assert len(products) == 3
    assert products[0]["product_name"] == "product_4"
    assert products[1]["product_name"] == "product_5"
    assert products[2]["product_name"] == "product_1"

@pytest.mark.asyncio
async def test_duplicate_mention_counts(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None
) -> None:
    """Should handle duplicate mention counts properly"""
    products = [
        {**single_product_ranking_row, "product_name": f"product_1", "mention_count": 100},
        {**single_product_ranking_row, "product_name": f"product_2", "mention_count": 100},
        {**single_product_ranking_row, "product_name": f"product_3", "mention_count": 22},
        {**single_product_ranking_row, "product_name": f"product_4", "mention_count": 999},
        {**single_product_ranking_row, "product_name": f"product_5", "mention_count": 200},
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
    
    response = await fastapi_client.client.get("/api/v1/category/topic_most_mentioned_product?product_topic=GPU")

    assert response.status_code == 200
    product_data = response.json()
    products = product_data["products"]

    assert len(products) == 3
    assert products[0]["product_name"] == "product_4"
    assert products[1]["product_name"] == "product_5"
    assert products[2]["product_name"] == "product_1"

@pytest.mark.asyncio
async def test_zero_mention_count(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None
) -> None:
    """Should return products even with 0 mention count"""
    products = [
        {**single_product_ranking_row, "product_name": f"product_1", "mention_count": 100},
        {**single_product_ranking_row, "product_name": f"product_2", "mention_count": 0},
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
    
    response = await fastapi_client.client.get("/api/v1/category/topic_most_mentioned_product?product_topic=GPU")

    assert response.status_code == 200
    product_data = response.json()
    products = product_data["products"]

    assert len(products) == 2
    assert products[0]["product_name"] == "product_1"
    assert products[1]["product_name"] == "product_2"