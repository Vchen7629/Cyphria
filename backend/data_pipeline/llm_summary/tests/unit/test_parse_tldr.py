from unittest.mock import Mock
from shared_core.logger import StructuredLogger
from src.llm_client.response_parser import parse_tldr
from src.llm_client.response_parser import TLDRValidationError
import pytest

logger = StructuredLogger(pod="llm_summary")


def test_raises_on_no_response() -> None:
    """No response should raise the TLDRValidationError"""
    with pytest.raises(TLDRValidationError, match="Empty response from LLM"):
        parse_tldr(response="  ", logger=logger)


def test_response_is_none() -> None:
    """input response none should raise the TLDRValidationError"""
    with pytest.raises(TLDRValidationError, match="Empty response from LLM"):
        parse_tldr(response=None, logger=logger)  # type: ignore


def test_multiple_prefixes_in_sequence() -> None:
    """Multiple prefixes in sequence should be replaced"""
    input = "TLDR: Summary: actual content"

    assert parse_tldr(response=input, logger=logger) == "actual content"


def test_prefix_case_insensitive() -> None:
    """prefix with mixed casing should be removed"""
    mixed_input = "tLdr: actual content"

    assert parse_tldr(response=mixed_input, logger=logger) == "actual content"


def test_prefix_appearing_mid_sentence() -> None:
    """Prefixes appearing mid-content should not be removed"""
    mixed_input = "This is important TLDR: actual content"

    assert parse_tldr(response=mixed_input, logger=logger) == mixed_input


def test_prefix_whitespace() -> None:
    """prefix with extra whitespace should be removed"""
    mixed_input = "TLDR:    actual content"

    assert parse_tldr(response=mixed_input, logger=logger) == "actual content"


def test_nested_quotes() -> None:
    """Nested quotes should be removed"""
    nested_double = '"content"'
    assert parse_tldr(response=nested_double, logger=logger) == "content"

    nested_single = "'content'"
    assert parse_tldr(response=nested_single, logger=logger) == "content"


def test_quotes_in_middle_of_content() -> None:
    """Quotes in middle of content should not be removed"""
    input = 'The "Important" summary'

    assert parse_tldr(response=input, logger=logger) == input


def test_only_one_quote() -> None:
    """Only one quote at beginning of content should be removed"""
    input = "'content"

    assert parse_tldr(response=input, logger=logger) == "content"


def test_word_boundaries() -> None:
    """Exactly 8 words or 16 words should not log"""
    mock_logger = Mock()

    lower_bound = "hi " * 8
    parse_tldr(response=lower_bound, logger=mock_logger)
    mock_logger.info.assert_not_called()

    mock_logger.reset_mock()
    upper_bound = "hi " * 16
    parse_tldr(response=upper_bound, logger=mock_logger)
    mock_logger.info.assert_not_called()
