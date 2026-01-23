from src.ingestion_service import IngestionService
import pytest

def test_no_job_state(mock_ingestion_service: IngestionService) -> None:
    """ValueError should be raised when no job_state is provided"""
    with pytest.raises(
        ValueError, 
        match="Job state must be provided for the run single cycle"
    ):
        mock_ingestion_service.run_single_cycle(job_state=None) # type: ignore
