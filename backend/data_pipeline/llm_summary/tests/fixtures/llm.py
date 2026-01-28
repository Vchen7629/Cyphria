from unittest.mock import MagicMock
import pytest


@pytest.fixture()
def mock_openai_client() -> MagicMock:
    """Mock OpenAi client and response"""
    mock_client = MagicMock()

    mock_response = MagicMock()
    mock_response.output_text = "TLDR: This is a test summary from the mock LLM client"

    mock_client.responses.create.return_value = mock_response

    return mock_client
