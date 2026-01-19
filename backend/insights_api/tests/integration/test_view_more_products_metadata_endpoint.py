import pytest
from tests.integration.conftest import FastAPITestClient

@pytest.mark.asyncio
async def test_time_window_90_day(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """view_more endpoint should return product metadata from database."""
    response = await fastapi_client.client.get(
        "/api/v1/product/view_more",
        params={"product_name": "nvidia rtx 4090", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product"]["positive_count"] == 100
    assert data["product"]["neutral_count"] == 10
    assert data["product"]["negative_count"] == 5

@pytest.mark.asyncio
async def test_time_window_all_time(fastapi_client: FastAPITestClient,seed_product_rankings: None) -> None:
    """view_more endpoint should return different data for all_time."""
    response = await fastapi_client.client.get(
        "/api/v1/product/view_more",
        params={"product_name": "nvidia rtx 4090", "time_window": "all_time"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product"]["positive_count"] == 200
    assert data["product"]["neutral_count"] == 20
    assert data["product"]["negative_count"] == 10

@pytest.mark.asyncio
async def test_case_insensitive(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """View more endpoint sql query should be case insensitive for product_name"""
    response = await fastapi_client.client.get(
        "/api/v1/product/view_more",
        params={"product_name": "NVIDIA RTX 4090", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product"]["positive_count"] == 100
    assert data["product"]["neutral_count"] == 10
    assert data["product"]["negative_count"] == 5

@pytest.mark.asyncio
async def test_product_name_whitespace(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """View more endpoint sql query should strip white space and match product_name"""
    response = await fastapi_client.client.get(
        "/api/v1/product/view_more",
        params={"product_name": "  NVIDIA RTX 4090  ", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product"]["positive_count"] == 100
    assert data["product"]["neutral_count"] == 10
    assert data["product"]["negative_count"] == 5

@pytest.mark.asyncio
async def test_invalid_time_window(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """view_more endpoint should return 422 if time_window is something other than all_time or 90d."""
    response_30d = await fastapi_client.client.get(
        "/api/v1/product/view_more",
        params={"product_name": "nvidia rtx 4090", "time_window": "30d"}
    )

    assert response_30d.status_code == 422

    response_7d = await fastapi_client.client.get(
        "/api/v1/product/view_more",
        params={"product_name": "nvidia rtx 4090", "time_window": "7d"}
    )

    assert response_7d.status_code == 422

    response_random_string = await fastapi_client.client.get(
        "/api/v1/product/view_more",
        params={"product_name": "nvidia rtx 4090", "time_window": "asdasd"}
    )

    assert response_random_string.status_code == 422

@pytest.mark.asyncio
async def test_product_name_not_found(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """view_more endpoint should return null product when not found."""
    response = await fastapi_client.client.get(
        "/api/v1/product/view_more",
        params={"product_name": "nonexistent product", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product"] is None

@pytest.mark.asyncio
async def test_missing_params(fastapi_client: FastAPITestClient) -> None:
    """view_more endpoint should return 422 when required params are missing."""
    response = await fastapi_client.client.get(
        "/api/v1/product/view_more",
        params={"time_window": "90d"}
    )
    assert response.status_code == 422

    response = await fastapi_client.client.get(
        "/api/v1/product/view_more",
        params={"product_name": "nvidia rtx 4090"}
    )
    assert response.status_code == 422