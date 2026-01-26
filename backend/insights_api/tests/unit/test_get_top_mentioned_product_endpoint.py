from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

@pytest.mark.parametrize(argnames="product_topic", argvalues=[None, "", "  "])
def test_invalid_product_topic_param(mock_fastapi: FastAPI, product_topic: str | None) -> None:
    """Invalid params for product_topic like None, empty string or whitespace should return 422"""
    with TestClient(mock_fastapi) as client:
        if product_topic is None:
            response = client.get("/api/v1/category/topic_most_mentioned_product")
        else:
            response = client.get(f"/api/v1/category/topic_most_mentioned_product?product_topic={product_topic}")

        assert response.status_code == 422
    
def test_no_top_products(mock_fastapi: FastAPI) -> None:
    """404 should be raised when top products list is not returned"""
    with patch("src.routes.category.fetch_topic_top_mentioned_products", return_value=[]):
        with TestClient(mock_fastapi) as client:
            response = client.get("api/v1/category/topic_most_mentioned_product?product_topic=GPU")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "top products not found for product_topic: GPU"