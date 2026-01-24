from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.schemas import RunRequest

def test_no_job_state(mock_fastapi: FastAPI) -> None:
    """No job state should raise a httpexception"""
    with patch("src.api.routes.job_state", None):
        app = mock_fastapi

        req_body = RunRequest(category="GPU", time_window="all_time")

        with TestClient(app) as client:
            response = client.post("/run", json=req_body.model_dump())
            assert response.status_code == 400
            assert response.json()["detail"] == "Missing job_state, cant trigger run"
