from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

@pytest.mark.parametrize(argnames="query", argvalues=[None,"", "  "])
def test_invalid_search_query_param(mock_fastapi: FastAPI, query: str | None) -> None:
    """Invalid params for query like None, empty string or whitespace should return 422"""
    with TestClient(mock_fastapi) as client:
        if query is None:
            response = client.get("/api/v1/product/search?q=&current_page=1")
        else:
            response = client.get(f"/api/v1/product/search?q={query}&current_page=1")

        assert response.status_code == 422

@pytest.mark.parametrize(argnames="current_page", argvalues=[None, 0, -1])
def test_invalid_current_page_param(mock_fastapi: FastAPI, current_page: int | None) -> None:
    """Invalid params for current_page like None, 0 or negative numbers invalid values should return 422"""
    with TestClient(mock_fastapi) as client:
        if current_page is None:
            response = client.get("/api/v1/product/search?q=hi&")
        else:
            response = client.get(f"/api/v1/product/search?q=huuuh&current_page={current_page}")

        assert response.status_code == 422
    
def test_no_search_results(mock_fastapi: FastAPI) -> None:
    """An empty array should be returned for no search results"""
    with patch("src.routes.products.fetch_matching_product_name", return_value=None):
        with TestClient(mock_fastapi) as client:
            response = client.get("/api/v1/product/search?q=huuuh&current_page=1")

            assert response.status_code == 200
            assert response.json()["products"] == []
            assert response.json()["current_page"] == 1
            assert response.json()["total_pages"] == 1

