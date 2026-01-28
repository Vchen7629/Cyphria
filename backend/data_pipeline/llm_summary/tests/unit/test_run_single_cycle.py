from src.summary_service import LLMSummaryService
import pytest


def test_no_job_state(mock_summary_service: LLMSummaryService) -> None:
    """ValueError should be raised when no job_state is provided"""
    with pytest.raises(ValueError, match="Job state must be provided for the run single cycle"):
        mock_summary_service.run_single_cycle(job_state=None)  # type: ignore
