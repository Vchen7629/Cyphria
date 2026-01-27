from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.types.fastapi import FastAPITestClient
import pytest


@pytest.mark.parametrize(argnames="time_window", argvalues=["90d", "all_time"])
@pytest.mark.asyncio
async def test_fetches_correct_time_window(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None,
    time_window: str,
) -> None:
    """It should only fetch the correct products for the time_window specified"""
    products = [
        {
            **single_product_ranking_row,
            "product_name": "product_1",
            "product_topic": "GPU",
            "time_window": "all_time",
            "rank": 1,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_2",
            "product_topic": "GPU",
            "time_window": "all_time",
            "rank": 2,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_3",
            "product_topic": "GPU",
            "time_window": "all_time",
            "rank": 3,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_4",
            "product_topic": "GPU",
            "time_window": "all_time",
            "rank": 4,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_5",
            "product_topic": "GPU",
            "time_window": "all_time",
            "rank": 5,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_1",
            "product_topic": "GPU",
            "time_window": "90d",
            "rank": 1,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_2",
            "product_topic": "GPU",
            "time_window": "90d",
            "rank": 2,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_3",
            "product_topic": "GPU",
            "time_window": "90d",
            "rank": 3,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_4",
            "product_topic": "GPU",
            "time_window": "90d",
            "rank": 4,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_5",
            "product_topic": "GPU",
            "time_window": "90d",
            "rank": 5,
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
        f"/api/v1/topic/products?product_topic=GPU&time_window={time_window}"
    )

    assert response.status_code == 200
    product_data = response.json()
    products = product_data["products"]

    assert len(products) == 5
    assert products[0]["product_name"] == "product_1"
    assert products[1]["product_name"] == "product_2"
    assert products[2]["product_name"] == "product_3"
    assert products[3]["product_name"] == "product_4"
    assert products[4]["product_name"] == "product_5"


@pytest.mark.asyncio
async def test_fetches_correct_product_topic(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None,
) -> None:
    """It should only fetch the correct products for the product topic specified"""
    products = [
        {
            **single_product_ranking_row,
            "product_name": "product_1",
            "product_topic": "GPU",
            "time_window": "all_time",
            "rank": 1,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_2",
            "product_topic": "CPU",
            "time_window": "all_time",
            "rank": 2,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_3",
            "product_topic": "GPU",
            "time_window": "all_time",
            "rank": 3,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_4",
            "product_topic": "CPU",
            "time_window": "all_time",
            "rank": 4,
        },
        {
            **single_product_ranking_row,
            "product_name": "product_5",
            "product_topic": "GPU",
            "time_window": "all_time",
            "rank": 5,
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
        "/api/v1/topic/products?product_topic=GPU&time_window=all_time"
    )

    assert response.status_code == 200
    product_data = response.json()
    products = product_data["products"]

    assert len(products) == 3
    assert products[0]["product_name"] == "product_1"
    assert products[1]["product_name"] == "product_3"
    assert products[2]["product_name"] == "product_5"
