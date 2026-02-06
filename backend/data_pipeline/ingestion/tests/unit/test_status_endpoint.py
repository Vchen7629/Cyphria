from datetime import timezone
from datetime import datetime
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.api.schemas import CurrentJob


def test_no_job_state(mock_fastapi: FastAPI) -> None:
    """No job state should raise a httpexception"""
    with patch("src.api.routes.job_state", None):
        app = mock_fastapi

        with TestClient(app) as client:
            response = client.get("/status")
            assert response.status_code == 400
            assert response.json()["detail"] == "Missing job_state, cant check status"


def test_current_job_returns_successfully(mock_fastapi: FastAPI) -> None:
    """When a job exists, it should return the job details"""
    with patch("src.api.routes.job_state") as mock_job_state:
        mock_job_state.get_current_job.return_value = CurrentJob(
            status="running", 
            subreddit_list=["Nvidia", "AMD"], 
            started_at=datetime.now(tz=timezone.utc),
            category="Computing"
        )

        app = mock_fastapi

        with TestClient(app) as client:
            response = client.get("/status")
            assert response.status_code == 200
            assert response.json()["status"] == "running"
