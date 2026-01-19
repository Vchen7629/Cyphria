import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.integration.conftest import FastAPITestClient

@pytest.mark.asyncio
async def test_success(fastapi_client: FastAPITestClient,seed_product_rankings: None) -> None:
    """get products by name endpoint should products including nvidia."""
    response = await fastapi_client.client.get("/api/v1/product/search?q=nvidia")

    assert response.status_code == 200
    data = response.json()
    comments = data["products"]

    assert len(comments) == 2

    # Should be ordered by score descending
    assert comments[0]["product_name"] == "nvidia rtx 4080"
    assert comments[1]["product_name"] == "nvidia rtx 4090"

@pytest.mark.asyncio
async def test_name_not_found(fastapi_client: FastAPITestClient, seed_raw_comments: None) -> None:
    """get products by name endpoint should return empty list for unknown product."""
    response = await fastapi_client.client.get("/api/v1/product/search?q=intel")

    assert response.status_code == 200
    data = response.json()
    assert data["products"] == []

@pytest.mark.asyncio
async def test_missing_search_param(fastapi_client: FastAPITestClient) -> None:
    """get products_by_name endpoint should return 422 when required params are missing."""
    response = await fastapi_client.client.get("/api/v1/product/search?q=")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_sql_injection(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """Search should be safe from SQL injection attempts."""
    response = await fastapi_client.client.get(
        "/api/v1/product/search",
        params={"q": "'; DROP TABLE product_rankings; --"}
    )

    assert response.status_code == 200
    data = response.json()
    # Should return empty list, not cause SQL error
    assert data["products"] == []

@pytest.mark.asyncio
async def test_sql_wildcard_percent(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """Search with % character should be treated literally, not as wildcard."""
    response = await fastapi_client.client.get(
        "/api/v1/product/search",
        params={"q": "%"}
    )

    assert response.status_code == 200
    data = response.json()
    # No product contains literal '%', should return empty
    assert data["products"] == []

@pytest.mark.asyncio
async def test_sql_wildcard_underscore(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """Search with _ character should be treated literally, not as single-char wildcard."""
    response = await fastapi_client.client.get(
        "/api/v1/product/search",
        params={"q": "_"}
    )

    assert response.status_code == 200
    data = response.json()
    # No product contains literal '_', should return empty
    assert data["products"] == []

@pytest.mark.asyncio
async def test_case_insensitive(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """Search should be case-insensitive due to ILIKE."""
    response = await fastapi_client.client.get(
        "/api/v1/product/search",
        params={"q": "NVIDIA"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) == 2

@pytest.mark.asyncio
async def test_whitespace_in_query(fastapi_client: FastAPITestClient, seed_product_rankings: None) -> None:
    """Search with internal whitespace should still find matches."""
    response = await fastapi_client.client.get(
        "/api/v1/product/search",
        params={"q": "rtx 4090"}
    )

    assert response.status_code == 200
    data = response.json()
    # Should find nvidia rtx 4090
    assert len(data["products"]) == 1
    assert data["products"][0]["product_name"] == "nvidia rtx 4090"

@pytest.mark.asyncio
async def test_returns_max_10_results(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    clean_tables: None
) -> None:
    """Search should return at most 10 results even when more match."""
    async with test_async_session() as session:
        # Insert 12 products with "gpu" in name
        values = ", ".join([
            f"('gpu model {i:02d}', 'GPU', '90d', {i}, 'A', 8.0, 100, 80, 80, 10, 10, false, false, false)"
            for i in range(1, 13)
        ])
        await session.execute(text(f"""
            INSERT INTO product_rankings
                (product_name, category, time_window, rank, grade, bayesian_score,
                 mention_count, approval_percentage, positive_count, neutral_count,
                 negative_count, is_top_pick, is_most_discussed, has_limited_data)
            VALUES {values}
        """))
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/product/search",
        params={"q": "gpu"}
    )

    assert response.status_code == 200
    data = response.json()

    # Should return only 10 even though 12 match
    assert len(data["products"]) == 10


@pytest.mark.asyncio
async def test_prefix_match_ordering(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    clean_tables: None
) -> None:
    """Search should order prefix matches before substring matches."""
    async with test_async_session() as session:
        await session.execute(text("""
            INSERT INTO product_rankings
                (product_name, category, time_window, rank, grade, bayesian_score,
                 mention_count, approval_percentage, positive_count, neutral_count,
                 negative_count, is_top_pick, is_most_discussed, has_limited_data)
            VALUES
                ('super rtx card', 'GPU', '90d', 1, 'A', 9.0, 100, 90, 90, 5, 5, false, false, false),
                ('rtx 4090', 'GPU', '90d', 2, 'A', 8.5, 100, 85, 85, 10, 5, false, false, false),
                ('rtx 4080', 'GPU', '90d', 3, 'A', 8.0, 100, 80, 80, 15, 5, false, false, false),
                ('my rtx setup', 'GPU', '90d', 4, 'B', 7.5, 100, 75, 75, 20, 5, false, false, false)
        """))
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/product/search",
        params={"q": "rtx"}
    )

    assert response.status_code == 200
    data = response.json()
    products = data["products"]

    assert len(products) == 4
    # Prefix matches (rtx 4080, rtx 4090) should come first, then substring matches
    assert products[0]["product_name"] == "rtx 4080"
    assert products[1]["product_name"] == "rtx 4090"
    # Substring matches come after
    assert products[2]["product_name"] in ["my rtx setup", "super rtx card"]
    assert products[3]["product_name"] in ["my rtx setup", "super rtx card"]
