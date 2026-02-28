from unittest.mock import MagicMock
from src.api.routes import get_job_state
from unittest.mock import patch
from datetime import datetime
from datetime import timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.schemas import CurrentJob
from src.api.schemas import RunRequest


def test_ready_endpoint(mock_fastapi: FastAPI) -> None:
    """Readiness endpoint should always return ready."""
    app = mock_fastapi

    with TestClient(app) as client:
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {"ready": True}


def test_no_job_state(mock_fastapi: FastAPI) -> None:
    """No job state should raise a httpexception"""
    mock_fastapi.dependency_overrides[get_job_state] = lambda: None

    req_body = RunRequest(
        category="Computing", topic_list=["GPU"], subreddit_list=["nvidia", "amd"]
    )

    with TestClient(mock_fastapi) as client:
        response = client.post("/run", json=req_body.model_dump())
        assert response.status_code == 400
        assert response.json()["detail"] == "Missing job_state, cant trigger run"


def test_current_job_returns_successfully(mock_fastapi: FastAPI) -> None:
    """When a job exists, it should return the job details"""
    mock_job_state = MagicMock()
    mock_job_state.get_current_job.return_value = CurrentJob(
        status="running",
        subreddit_list=["Nvidia", "AMD"],
        started_at=datetime.now(tz=timezone.utc),
        category="Computing",
    )

    mock_fastapi.dependency_overrides[get_job_state] = lambda: mock_job_state

    with TestClient(mock_fastapi) as client:
        response = client.get("/status")
        assert response.status_code == 200
        assert response.json()["status"] == "running"

    mock_fastapi.dependency_overrides.clear()