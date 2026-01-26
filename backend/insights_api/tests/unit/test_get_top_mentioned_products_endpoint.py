from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

@pytest.mark.parametrize(argnames="category", argvalues=[None, "", "  "])
def test_invalid_category_param(mock_fastapi: FastAPI, category: str | None) -> None:
    """Invalid params for category like None, empty string or whitespace should return 422"""
    with TestClient(mock_fastapi) as client:
        if category is None:
            response = client.get("/api/v1/category/top_mentioned_products")
        else:
            response = client.get(f"/api/v1/category/top_mentioned_products?category={category}")

        assert response.status_code == 422
    
def test_no_category_topics(mock_fastapi: FastAPI) -> None:
    """404 should be raised when topic list is not returned"""
    with patch("src.routes.category.get_topics_for_category", return_value=[]), \
         patch("src.routes.category.get_cache_value") as mock_get_cache:
        with TestClient(mock_fastapi) as client:
            response = client.get("api/v1/category/top_mentioned_products?category=gaming")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "topics not found for category: gaming"
            mock_get_cache.assert_not_called()

def test_no_top_mentioned_products(mock_fastapi: FastAPI) -> None:
    """404 should be raised when top mentioned products isnt returned"""
    with patch("src.routes.category.fetch_top_mentioned_products", return_value=[]), \
         patch("src.routes.category.set_cache_value") as mock_get_cache:
        with TestClient(mock_fastapi) as client:
            response = client.get("api/v1/category/top_mentioned_products?category=gaming")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "top products not found for category: gaming"
            mock_get_cache.assert_not_called()