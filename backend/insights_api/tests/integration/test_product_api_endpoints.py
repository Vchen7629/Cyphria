import pytest
from tests.integration.conftest import FastAPITestClient


@pytest.mark.asyncio
async def test_get_view_more_products_metadata_success(
    fastapi_client: FastAPITestClient,
    seed_product_rankings: None
) -> None:
    """view_more endpoint should return product metadata from database."""
    response = await fastapi_client.client.get(
        "/api/v1/products/view_more",
        params={"product_name": "nvidia rtx 4090", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product"]["positive_count"] == 100
    assert data["product"]["neutral_count"] == 10
    assert data["product"]["negative_count"] == 5


@pytest.mark.asyncio
async def test_get_top_comments_success(
    fastapi_client: FastAPITestClient,
    seed_raw_comments: None
) -> None:
    """top_comments endpoint should return top 5 comments ordered by score."""
    response = await fastapi_client.client.get(
        "/api/v1/products/top_comments",
        params={"product_name": "nvidia rtx 4090", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    # Should return 3 comments (within 90d and sentiment_processed=true)
    assert len(comments) == 3

    # Should be ordered by score descending
    assert comments[0]["score"] == 150
    assert comments[1]["score"] == 100
    assert comments[2]["score"] == 75

@pytest.mark.asyncio
async def test_get_view_more_products_metadata_all_time(
    fastapi_client: FastAPITestClient,
    seed_product_rankings: None
) -> None:
    """view_more endpoint should return different data for all_time."""
    response = await fastapi_client.client.get(
        "/api/v1/products/view_more",
        params={"product_name": "nvidia rtx 4090", "time_window": "all_time"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product"]["positive_count"] == 200
    assert data["product"]["neutral_count"] == 20
    assert data["product"]["negative_count"] == 10

@pytest.mark.asyncio
async def test_get_top_comments_all_time(
    fastapi_client: FastAPITestClient,
    seed_raw_comments: None
) -> None:
    """top_comments endpoint with all_time should include older comments."""
    response = await fastapi_client.client.get(
        "/api/v1/products/top_comments",
        params={"product_name": "nvidia rtx 4090", "time_window": "all_time"}
    )

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    # Should return 4 comments (all sentiment_processed=true, regardless of date)
    assert len(comments) == 4

    # Should be ordered by score descending - comment_4 has highest score (200)
    assert comments[0]["score"] == 200

@pytest.mark.asyncio
async def test_get_view_more_products_metadata_not_found(
    fastapi_client: FastAPITestClient,
    seed_product_rankings: None
) -> None:
    """view_more endpoint should return null product when not found."""
    response = await fastapi_client.client.get(
        "/api/v1/products/view_more",
        params={"product_name": "nonexistent product", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product"] is None


@pytest.mark.asyncio
async def test_get_view_more_products_metadata_missing_params(
    fastapi_client: FastAPITestClient
) -> None:
    """view_more endpoint should return 422 when required params are missing."""
    response = await fastapi_client.client.get(
        "/api/v1/products/view_more",
        params={"time_window": "90d"}
    )
    assert response.status_code == 422

    response = await fastapi_client.client.get(
        "/api/v1/products/view_more",
        params={"product_name": "nvidia rtx 4090"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_top_comments_empty_result(
    fastapi_client: FastAPITestClient,
    seed_raw_comments: None
) -> None:
    """top_comments endpoint should return empty list for unknown product."""
    response = await fastapi_client.client.get(
        "/api/v1/products/top_comments",
        params={"product_name": "nonexistent product", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["top_comments"] == []
