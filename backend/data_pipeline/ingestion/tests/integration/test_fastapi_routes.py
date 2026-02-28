from unittest.mock import patch
from unittest.mock import MagicMock
from src.api.schemas import RunRequest
from src.api.schemas import IngestionResult
from tests.utils.classes import FastAPITestClient


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
    with patch("src.api.routes.IngestionService") as MockService:
        mock_instance = MagicMock()
        mock_instance.run_ingestion_pipeline.return_value = IngestionResult(
            posts_processed=10,
            comments_processed=100,
            comments_inserted=50,
            cancelled=False,
        )
        MockService.return_value = mock_instance
        req_body = RunRequest(category="Computing", topic_list=["GPU"], subreddit_list=["nvidia"])

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"


def test_call_run_endpoint_when_already_in_progress(
    fastapi_client: FastAPITestClient, mock_job: MagicMock
) -> None:
    """Run endpoint should return 409 when run already in progress"""
    job_state = fastapi_client.app.state.job_state
    job_state.set_running_job(mock_job)

    try:
        req_body = RunRequest(category="Computing", topic_list=["GPU"], subreddit_list=["nvidia"])

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 409
        assert "already in progress" in response.json()["detail"]
    finally:
        job_state.mark_complete(
            IngestionResult(
                posts_processed=0, comments_processed=0, comments_inserted=0, cancelled=False
            )
        )
