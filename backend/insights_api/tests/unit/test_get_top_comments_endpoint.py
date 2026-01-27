from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest


@pytest.mark.parametrize(argnames="product_name", argvalues=[None, "", "  "])
def test_invalid_product_name_param(
    mock_fastapi: FastAPI, product_name: str | None
) -> None:
    """Invalid params for product name like None, empty string or whitespace should return 422"""
    with TestClient(mock_fastapi) as client:
        if product_name is None:
            response = client.get("/api/v1/product/top_comments?time_window=all_time")
        else:
            response = client.get(
                f"/api/v1/product/top_comments?product_name={product_name}&time_window=all_time"
            )

        assert response.status_code == 422


@pytest.mark.parametrize(argnames="time_window", argvalues=[None, "", "  "])
def test_invalid_time_window_param(
    mock_fastapi: FastAPI, time_window: str | None
) -> None:
    """Invalid params for time_window like None, empty string or whitespace should return 422"""
    with TestClient(mock_fastapi) as client:
        if time_window is None:
            response = client.get("/api/v1/product/top_comments?product_name=dog")
        else:
            response = client.get(
                f"/api/v1/product/top_comments?product_name=dog&time_window={time_window}"
            )

        assert response.status_code == 422


def test_no_top_comments(mock_fastapi: FastAPI) -> None:
    """404 should be raised when top_comments list is not returned"""
    with patch("src.routes.products.fetch_top_reddit_comments", return_value=[]):
        with TestClient(mock_fastapi) as client:
            response = client.get(
                "api/v1/product/top_comments?product_name=dog&time_window=all_time"
            )

            assert response.status_code == 404
            assert (
                response.json()["detail"]
                == "No reddit comments found for product: dog and time_window: all_time"
            )
