from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest


@pytest.mark.parametrize(argnames="product_topic", argvalues=[None, "", "  "])
def test_invalid_product_topic_param(
    mock_fastapi: FastAPI, product_topic: str | None
) -> None:
    """Invalid params for product_topic like None, empty string or whitespace should return 422"""
    with TestClient(mock_fastapi) as client:
        if product_topic is None:
            response = client.get("/api/v1/topic/total_comments?&time_window=all_time")
        else:
            response = client.get(
                f"/api/v1/topic/total_comments?product_topic={product_topic}&time_window=all_time"
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
            response = client.get("/api/v1/topic/total_comments?product_topic=huuuh")
        else:
            response = client.get(
                f"/api/v1/topic/total_comments?product_topic=huuuh&time_window={time_window}"
            )

        assert response.status_code == 422
