from fastapi.testclient import TestClient
from fastapi import FastAPI


def test_ready_endpoint(mock_fastapi: FastAPI) -> None:
    """Readiness endpoint should always return ready."""
    app = mock_fastapi

    with TestClient(app) as client:
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {"ready": True}
