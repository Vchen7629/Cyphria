import pytest
from tests.integration.conftest import FastAPITestClient

@pytest.mark.asyncio
async def test_time_window_90_day(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """ranked products endpoint should return products with 90 day time window"""
    response = await fastapi_client.client.get(
        "/api/v1/category/products",
        params={"category": "GPU", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()["products"]
    assert len(data) == 3
    assert data[0]["product_name"] == "nvidia rtx 4090"
    assert data[1]["product_name"] == "nvidia rtx 4080"
    assert data[2]["product_name"] == "amd rx 7900 xtx"

@pytest.mark.asyncio
async def test_time_window_all_time(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """Ranked products endpoint should return products with all_time time window"""
    response = await fastapi_client.client.get(       
        "/api/v1/category/products",
        params={"category": "GPU", "time_window": "all_time"}
    )

    assert response.status_code == 200
    data = response.json()["products"]
    assert len(data) == 1
    assert data[0]["product_name"] == "nvidia rtx 4090"

@pytest.mark.asyncio
async def test_category_case_insensitive(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """Ranked products endpoint category param should be case insensitive and match"""
    response = await fastapi_client.client.get(       
        "/api/v1/category/products",
        params={"category": "gPu", "time_window": "all_time"}
    )

    assert response.status_code == 200
    data = response.json()["products"]
    assert len(data) == 1
    assert data[0]["product_name"] == "nvidia rtx 4090"

@pytest.mark.asyncio
async def test_category_whitespace(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """Ranked products endpoint should strip whitespace and match for category param"""
    response = await fastapi_client.client.get(       
        "/api/v1/category/products",
        params={"category": "  GPU  ", "time_window": "all_time"}
    )

    assert response.status_code == 200
    data = response.json()["products"]
    assert len(data) == 1
    assert data[0]["product_name"] == "nvidia rtx 4090"

@pytest.mark.asyncio
async def test_invalid_time_window(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """Ranked products endpoint should return 422 if time_window is something other than all_time or 90d."""
    response_30d = await fastapi_client.client.get(
        "/api/v1/category/products",
        params={"category": "GPU", "time_window": "30d"}
    )

    assert response_30d.status_code == 422

    response_7d = await fastapi_client.client.get(
        "/api/v1/category/products",
        params={"category": "GPU", "time_window": "7d"}
    )

    assert response_7d.status_code == 422

    response_random_string = await fastapi_client.client.get(
        "/api/v1/category/products",
        params={"category": "GPU", "time_window": "asdasd"}
    )

    assert response_random_string.status_code == 422

@pytest.mark.asyncio
async def test_category_not_found(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """Ranked products endpoint should return an empty list if the category isnt found"""
    response = await fastapi_client.client.get(       
        "/api/v1/category/products",
        params={"category": "invalid", "time_window": "all_time"}
    )

    assert response.status_code == 200
    data = response.json()["products"]
    assert data == []

@pytest.mark.asyncio
async def test_missing_params(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """Ranked products endpoint should return 422 if either category or time_window params are missing"""
    no_category_response = await fastapi_client.client.get(       
        "/api/v1/category/products",
        params={"time_window": "all_time"}
    )

    assert no_category_response.status_code == 422

    no_time_window_response = await fastapi_client.client.get(       
        "/api/v1/category/products",
        params={"category": "GPU"}
    )

    assert no_time_window_response.status_code == 422
    
