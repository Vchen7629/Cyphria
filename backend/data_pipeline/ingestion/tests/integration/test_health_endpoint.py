from unittest.mock import MagicMock
from tests.utils.classes import FastAPITestClient


def test_health_endpoint_health_when_dependencies_ok(fastapi_client: FastAPITestClient) -> None:
    """Health endpoint should return healthy when all dependencies ok"""
    response = fastapi_client.client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["db_connected"] is True


def test_health_endpoint_unhealthy_db(fastapi_client: FastAPITestClient) -> None:
    """Health endpoint should return unhealthy when DB fails"""
    fastapi_client.app.state.db_pool = MagicMock()
    fastapi_client.app.state.db_pool.connection.side_effect = Exception("DB error")

    response = fastapi_client.client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["db_connected"] is False
