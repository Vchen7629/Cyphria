from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest


@pytest.mark.parametrize(argnames="product_name", argvalues=[None, "", "  "])
def test_invalid_product_name_param(
    mock_fastapi: FastAPI, product_name: str | None
) -> None:
    """Invalid params for product_name like None, empty string or whitespace should return 422"""
    with TestClient(mock_fastapi) as client:
        if product_name is None:
            response = client.get(
                "/api/v1/product/sentiment_scores?&time_window=all_time"
            )
        else:
            response = client.get(
                f"/api/v1/product/sentiment_scores?product_name={product_name}&time_window=all_time"
            )

        assert response.status_code == 422


@pytest.mark.parametrize(
    argnames="time_window", argvalues=[None, "", "  ", "30d", "365s"]
)
def test_invalid_time_window_param(
    mock_fastapi: FastAPI, time_window: str | None
) -> None:
    """Invalid params for time_window like None, empty string, whitespace, or invalid values should return 422"""
    with TestClient(mock_fastapi) as client:
        if time_window is None:
            response = client.get("/api/v1/product/sentiment_scores?product_name=huuuh")
        else:
            response = client.get(
                f"/api/v1/product/sentiment_scores?product_name=huuuh&time_window={time_window}"
            )

        assert response.status_code == 422


def test_no_sentiment_scores_topics(mock_fastapi: FastAPI) -> None:
    """404 should be raised when topic list is not returned"""
    with patch("src.routes.products.fetch_product_sentiment_scores", return_value=None):
        with TestClient(mock_fastapi) as client:
            response = client.get(
                "/api/v1/product/sentiment_scores?product_name=huuuh&time_window=all_time"
            )

            assert response.status_code == 404
            assert (
                response.json()["detail"]
                == "Sentiment counts not found for product: huuuh time_window: all_time"
            )
