from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime
from datetime import timezone
from unittest.mock import MagicMock
from src.api.routes import get_job_state
from src.api.schemas import CurrentJob


def test_ready_endpoint(mock_fastapi: FastAPI) -> None:
    """Readiness endpoint should always return ready."""
    app = mock_fastapi

    with TestClient(app) as client:
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {"ready": True}


def test_status_no_job_state(mock_fastapi: FastAPI) -> None:
    """No job state should raise a httpexception"""
    mock_fastapi.dependency_overrides[get_job_state] = lambda: None

    with TestClient(mock_fastapi) as client:
        response = client.get("/status")
        assert response.status_code == 400
        assert response.json()["detail"] == "Missing job_state, cant fetch status"


def test_current_job_returns_successfully(mock_fastapi: FastAPI) -> None:
    """When a job exists, it should return the job details"""
    mock_job_state = MagicMock()
    mock_job_state.get_current_job.return_value = CurrentJob(
        status="running",
        product_topic="GPU",
        started_at=datetime.now(tz=timezone.utc),
        category="Computing",
    )

    mock_fastapi.dependency_overrides[get_job_state] = lambda: mock_job_state

    with TestClient(mock_fastapi) as client:
        response = client.get("/status")
        assert response.status_code == 200
        assert response.json()["status"] == "running"

    mock_fastapi.dependency_overrides.clear()
