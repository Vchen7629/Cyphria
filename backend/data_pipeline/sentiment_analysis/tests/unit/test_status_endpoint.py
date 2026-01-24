from datetime import timezone
from datetime import datetime
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.schemas import CurrentJob

def test_no_job_state(mock_fastapi: FastAPI) -> None:
    """No job state should raise a httpexception"""
    with patch("src.api.routes.job_state", None):
        app = mock_fastapi

        with TestClient(app) as client:
            response = client.get("/status")
            assert response.status_code == 400
            assert response.json()["detail"] == "Missing job_state, cant fetch status"

def test_no_current_job(mock_fastapi: FastAPI) -> None:
    """If not current job, it should raise 404 error"""
    # Create minimal FastAPI app with just the routes we need
    with patch("src.api.routes.job_state") as mock_job_state:
        mock_job_state.get_current_job.return_value = None

        # Import router after patching to ensure mock is in place
        from src.api.routes import router

        app = mock_fastapi

        with TestClient(app) as client:
            response = client.get("/status")
            assert response.status_code == 404
            assert response.json()["detail"] == "Job not found"


def test_current_job_returns_successfully(mock_fastapi: FastAPI) -> None:
    """When a job exists, it should return the job details"""
    with patch("src.api.routes.job_state") as mock_job_state:
        mock_job_state.get_current_job.return_value = CurrentJob(
            status="running",
            category="GPU",
            started_at=datetime.now(tz=timezone.utc)
        )

        app = mock_fastapi

        with TestClient(app) as client:
            response = client.get("/status")
            assert response.status_code == 200
            assert response.json()["status"] == "running"
            assert response.json()["category"] == "GPU"


