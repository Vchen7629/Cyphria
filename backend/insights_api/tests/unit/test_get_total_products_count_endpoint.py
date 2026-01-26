from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

@pytest.mark.parametrize(argnames="category", argvalues=[None, "", "  "])
def test_invalid_category_param(mock_fastapi: FastAPI, category: str | None) -> None:
    """Invalid params for category like None, empty string or whitespace should return 422"""
    with TestClient(mock_fastapi) as client:
        if category is None:
            response = client.get("/api/v1/category/total_products_count")
        else:
            response = client.get(f"/api/v1/category/total_products_count?category={category}")

        assert response.status_code == 422
    
def test_no_category_topics(mock_fastapi: FastAPI) -> None:
    """404 should be raised when topic list is not returned"""
    with patch("src.routes.category.get_topics_for_category", return_value=[]):
        with TestClient(mock_fastapi) as client:
            response = client.get("api/v1/category/total_products_count?category=gaming")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "topics not found for category: gaming"