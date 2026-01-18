from src.api.schemas import RunRequest
from unittest.mock import patch
from unittest.mock import MagicMock
from tests.integration.conftest import FastAPITestClient
from src.api.schemas import IngestionResult
from src.api.signal_handler import run_state

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

def test_ready_endpoint(fastapi_client: FastAPITestClient) -> None:
    """Readiness endpoint should always return ready."""
    response = fastapi_client.client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"ready": True}

def test_run_endpoint_success(fastapi_client: FastAPITestClient) -> None:
    """Run endpoint should complete successfully with mocked ingestion."""
    with patch('src.api.routes.IngestionService') as MockService:
        mock_instance = MagicMock()
        mock_instance.run.return_value = IngestionResult(
            posts_processed=10,
            comments_processed=100,
            comments_inserted=50,
            cancelled=False,
        )
        MockService.return_value = mock_instance

        req_body = RunRequest(
            category="GPU",
            subreddits=["nvidia"]
        )

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["result"]["posts_processed"] == 10
        assert data["result"]["comments_inserted"] == 50

def test_call_run_endpoint_when_already_in_progress(fastapi_client: FastAPITestClient) -> None:
    """Run endpoint should return 409 when run already in progress"""
    original_value = run_state.run_in_progress
    run_state.run_in_progress = True

    try:
        req_body = RunRequest(
            category="GPU",
            subreddits=["nvidia"]
        )

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 409
        assert "already in progress" in response.json()["detail"]
    finally:
        run_state.run_in_progress = original_value

def test_run_endpoint_error_handling(fastapi_client: FastAPITestClient) -> None:
    """Run endpoint should handle error gracefully"""
    with patch('src.api.routes.IngestionService') as MockService:
        mock_instance = MagicMock()
        mock_instance.run.side_effect = Exception("Reddit API error")
        MockService.return_value = mock_instance

        req_body = RunRequest(
            category="GPU",
            subreddits=["nvidia"]
        )

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 500
        data = response.json()
        assert "Reddit API error" in data["detail"]