from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch


def test_no_job_state(mock_fastapi: FastAPI) -> None:
    """No job state should raise a httpexception"""
    with patch("src.api.routes.job_state", None):
        app = mock_fastapi

        with TestClient(app) as client:
            response = client.get("/status")
            assert response.status_code == 400
            assert response.json()["detail"] == "Missing job_state, cant fetch status"
