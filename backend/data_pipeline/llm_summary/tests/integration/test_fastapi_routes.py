from unittest.mock import patch
from unittest.mock import MagicMock
from tests.types.fastapi import FastAPITestClient
from src.api.schemas import RunRequest
from src.api.schemas import SummaryResult

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

def test_run_endpoint_success(fastapi_client: FastAPITestClient) -> None:
    """Run endpoint should return status: started."""
    with patch("src.api.routes.LLMSummaryService") as MockService:
        mock_instance = MagicMock()
        mock_instance.run.return_value = SummaryResult(
            products_summarized=10,
            cancelled=False,
        )
        MockService.return_value = mock_instance

        req_body = RunRequest(time_window="all_time")

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"


def test_call_run_endpoint_when_already_in_progress(
    fastapi_client: FastAPITestClient, mock_job: MagicMock
) -> None:
    """Run endpoint should return 409 when run already in progress"""
    # Create a running job to trigger the 409 response
    job_state = fastapi_client.app.state.job_state
    job_state.set_running_job(mock_job)

    try:
        req_body = RunRequest(time_window="all_time")

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 409
        assert "already in progress" in response.json()["detail"]
    finally:
        # Clean up by completing the job
        job_state.mark_complete(
            SummaryResult(products_summarized=10, cancelled=False)
        )
