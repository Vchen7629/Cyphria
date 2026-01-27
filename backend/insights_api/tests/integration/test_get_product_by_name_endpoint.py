from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.types.fastapi import FastAPITestClient
import pytest


@pytest.mark.asyncio
async def test_success(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None,
) -> None:
    """Searching a product with matching name should return it."""
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
        "/api/v1/product/search?q=nvidia&current_page=1"
    )

    assert response.status_code == 200
    data = response.json()
    products = data["products"]
    current_page = data["current_page"]
    total_pages = data["total_pages"]

    assert len(products) == 1
    assert current_page == 1
    assert total_pages == 1

    # Should be ordered by score descending
    assert products[0]["product_name"] == "nvidia rtx 4080"


@pytest.mark.asyncio
async def test_prefix_match_ordering(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None,
) -> None:
    """Search should order prefix matches before substring matches."""
    products = [
        {**single_product_ranking_row, "product_name": "super rtx card"},
        {**single_product_ranking_row, "product_name": "rtx 4090"},
        {**single_product_ranking_row, "product_name": "rtx 4080"},
        {**single_product_ranking_row, "product_name": "my rtx setup"},
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
        "/api/v1/product/search?q=rtx&current_page=1"
    )

    assert response.status_code == 200
    data = response.json()
    products = data["products"]
    current_page = data["current_page"]
    total_pages = data["total_pages"]

    assert len(products) == 4
    assert current_page == 1
    assert total_pages == 1

    # Prefix matches (rtx 4080, rtx 4090) should come first, then substring matches
    assert products[0]["product_name"] == "rtx 4080"
    assert products[1]["product_name"] == "rtx 4090"
    # Substring matches come after
    assert products[2]["product_name"] in ["my rtx setup", "super rtx card"]
    assert products[3]["product_name"] in ["my rtx setup", "super rtx card"]


@pytest.mark.asyncio
async def test_search_non_existing_product_name(
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
        "/api/v1/product/search?q=auuugh&current_page=1"
    )

    assert response.status_code == 200
    data = response.json()
    products = data["products"]
    current_page = data["current_page"]
    total_pages = data["total_pages"]

    assert len(products) == 0
    assert current_page == 1
    assert total_pages == 1


@pytest.mark.asyncio
async def test_correct_page_values(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None,
) -> None:
    """It should return the correct values for the specified page"""
    products = [
        {**single_product_ranking_row, "product_name": f"gpu {i}"} for i in range(20)
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

    first_page_res = await fastapi_client.client.get(
        "/api/v1/product/search?q=gpu&current_page=1"
    )

    assert first_page_res.status_code == 200
    first_page_data = first_page_res.json()
    first_page_products = first_page_data["products"]
    first_page_current_page = first_page_data["current_page"]
    first_page_total_pages = first_page_data["total_pages"]

    assert len(first_page_products) == 6
    assert first_page_current_page == 1
    assert first_page_total_pages == 4

    assert first_page_products[0]["product_name"] == "gpu 0"
    assert first_page_products[1]["product_name"] == "gpu 1"
    assert first_page_products[2]["product_name"] == "gpu 10"
    assert first_page_products[3]["product_name"] == "gpu 11"
    assert first_page_products[4]["product_name"] == "gpu 12"
    assert first_page_products[5]["product_name"] == "gpu 13"

    third_page_res = await fastapi_client.client.get(
        "/api/v1/product/search?q=gpu&current_page=3"
    )
    assert third_page_res.status_code == 200
    third_page_data = third_page_res.json()
    third_page_products = third_page_data["products"]
    third_page_current_page = third_page_data["current_page"]
    third_page_total_pages = third_page_data["total_pages"]

    assert len(third_page_products) == 6
    assert third_page_current_page == 3
    assert third_page_total_pages == 4

    assert third_page_products[0]["product_name"] == "gpu 2"
    assert third_page_products[1]["product_name"] == "gpu 3"
    assert third_page_products[2]["product_name"] == "gpu 4"
    assert third_page_products[3]["product_name"] == "gpu 5"
    assert third_page_products[4]["product_name"] == "gpu 6"
    assert third_page_products[5]["product_name"] == "gpu 7"


@pytest.mark.asyncio
async def test_cache_hit(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    single_product_ranking_row: dict[str, Any],
    clean_tables: None,
) -> None:
    """If cache key is found, it should use the value from the cache instead of calling db"""
