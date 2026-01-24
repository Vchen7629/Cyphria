from unittest.mock import patch
from unittest.mock import MagicMock
from src.api import routes
from src.api.schemas import RunRequest
from src.api.schemas import RankingResult
from tests.types.fastapi import FastAPITestClient

def test_run_endpoint_success(fastapi_client: FastAPITestClient) -> None:
    """Run endpoint should return status: started."""
    with patch('src.api.routes.RankingService') as MockService:
        mock_instance = MagicMock()
        mock_instance.run.return_value = RankingResult(
            products_processed=10,
            cancelled=False,
        )
        MockService.return_value = mock_instance

        req_body = RunRequest(category="GPU", time_window="all_time")

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        
def test_call_run_endpoint_when_already_in_progress(fastapi_client: FastAPITestClient) -> None:
    """Run endpoint should return 409 when run already in progress"""
    # Create a running job to trigger the 409 response
    routes.job_state.create_job("GPU")

    try:
        req_body = RunRequest(category="GPU", time_window="all_time")

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 409
        assert "already in progress" in response.json()["detail"]
    finally:
        # Clean up by completing the job
        routes.job_state.complete_job(RankingResult(
            products_processed=10,
            cancelled=False
        ))
