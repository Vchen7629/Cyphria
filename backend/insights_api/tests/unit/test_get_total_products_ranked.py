from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest


@pytest.mark.parametrize(argnames="product_topic", argvalues=[None, "", "  "])
def test_invalid_product_topic_param(
    mock_fastapi: FastAPI, product_topic: str | None
) -> None:
    """Invalid params for product topic like None, empty string or whitespace should return 422"""
    with TestClient(mock_fastapi) as client:
        if product_topic is None:
            response = client.get("/api/v1/topic/total_products_ranked?")
        else:
            response = client.get(
                f"/api/v1/topic/total_products_ranked?product_topic={product_topic}"
            )

        assert response.status_code == 422
