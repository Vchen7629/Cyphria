from src.sentiment_service import SentimentService
import pytest

def test_no_job_state(mock_sentiment_service: SentimentService) -> None:
    """ValueError should be raised when no job_state is provided"""
    with pytest.raises(
        ValueError, 
        match="Job state must be provided for the run single cycle"
    ):
        mock_sentiment_service.run_single_cycle(job_state=None) # type: ignore
