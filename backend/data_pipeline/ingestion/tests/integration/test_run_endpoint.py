from _operator import sub
from unittest.mock import patch
from unittest.mock import MagicMock
from src.api import routes
from src.api.schemas import RunRequest
from src.api.schemas import IngestionResult
from tests.utils.classes import FastAPITestClient


def test_run_endpoint_success(fastapi_client: FastAPITestClient) -> None:
    """Run endpoint should return status: started."""
    with patch("src.api.routes.IngestionService") as MockService, \
         patch("src.api.routes.DetectorFactory.get_detector") as mock_get_detector:
        mock_instance = MagicMock()
        mock_instance.run_single_cycle.return_value = IngestionResult(
            posts_processed=10,
            comments_processed=100,
            comments_inserted=50,
            cancelled=False,
        )
        MockService.return_value = mock_instance

        mock_detector = MagicMock()
        mock_get_detector.return_value = mock_detector

        req_body = RunRequest(category="Computing" ,topic_list=["GPU"], subreddit_list=["nvidia"])

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"


def test_call_run_endpoint_when_already_in_progress(fastapi_client: FastAPITestClient) -> None:
    """Run endpoint should return 409 when run already in progress"""
    job_state = routes.job_state
    assert job_state is not None
    job_state.create_job(category="Computing", subreddit_list=["nvidia"])

    try:
        req_body = RunRequest(category="Computing", topic_list=["GPU"], subreddit_list=["nvidia"])

        response = fastapi_client.client.post("/run", json=req_body.model_dump())

        assert response.status_code == 409
        assert "already in progress" in response.json()["detail"]
    finally:
        job_state.complete_job(
            IngestionResult(
                posts_processed=0, comments_processed=0, comments_inserted=0, cancelled=False
            )
        )
