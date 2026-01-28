from unittest.mock import patch
from unittest.mock import MagicMock
from src.api import routes
from src.api.schemas import RunRequest
from src.api.schemas import SentimentResult
from tests.types.fastapi import FastAPITestClient


def test_run_endpoint_success(fastapi_client: FastAPITestClient) -> None:
    """Run endpoint should return status: started."""
    with patch("src.api.routes.SentimentService") as MockService:
        mock_instance = MagicMock()
        mock_instance.run.return_value = SentimentResult(
            comments_inserted=10,
            comments_updated=10,
            cancelled=False,
        )
        MockService.return_value = mock_instance

        req_body = RunRequest(product_topic="GPU")

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"


def test_call_run_endpoint_when_already_in_progress(fastapi_client: FastAPITestClient) -> None:
    """Run endpoint should return 409 when run already in progress"""
    # Create a running job to trigger the 409 response
    job_state = routes.job_state
    assert job_state is not None

    job_state.create_job("GPU")

    try:
        req_body = RunRequest(product_topic="GPU")

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 409
        assert "already in progress" in response.json()["detail"]
    finally:
        # Clean up by completing the job
        job_state.complete_job(
            SentimentResult(
                comments_inserted=10,
                comments_updated=10,
                cancelled=False,
            )
        )
