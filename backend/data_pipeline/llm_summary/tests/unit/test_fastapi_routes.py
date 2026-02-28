from datetime import timezone
from datetime import datetime
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.api.schemas import CurrentJob
from src.api.schemas import RunRequest
from src.api.routes import get_job_state

def test_no_job_state(mock_fastapi: FastAPI) -> None:
    """No job state should raise a httpexception"""
    mock_fastapi.dependency_overrides[get_job_state] = lambda: None

    req_body = RunRequest(time_window="all_time")

    with TestClient(mock_fastapi) as client:
        response = client.post("/run", json=req_body.model_dump())
        assert response.status_code == 400
        assert response.json()["detail"] == "Missing job_state, cant trigger run"

def test_current_job_returns_successfully(mock_fastapi: FastAPI) -> None:
    """When a job exists, it should return the job details"""
    mock_job_state = MagicMock()
    mock_job_state.get_current_job.return_value = CurrentJob(
        status="running", 
        time_window="all_time", 
        started_at=datetime.now(tz=timezone.utc)
    )

    mock_fastapi.dependency_overrides[get_job_state] = lambda: mock_job_state

    with TestClient(mock_fastapi) as client:
        response = client.get("/status")
        assert response.status_code == 200
        assert response.json()["status"] == "running"
        assert response.json()["time_window"] == "all_time"
    
    mock_fastapi.dependency_overrides.clear()

def test_ready_endpoint(mock_fastapi: FastAPI) -> None:
    """Readiness endpoint should always return ready."""
    app = mock_fastapi

    with TestClient(app) as client:
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {"ready": True}
