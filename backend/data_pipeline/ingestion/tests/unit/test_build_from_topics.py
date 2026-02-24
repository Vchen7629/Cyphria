from unittest.mock import patch
from src.product_detector.base import BuildDetectorRegex
import pytest

build_regex = BuildDetectorRegex()

@pytest.mark.parametrize(argnames="product_topic", argvalues=[None, "", "  "])
def test_invalid_input_product_topic(product_topic: str | None) -> None:
    """Invalid product topic param (None, empty string, whitespace) should return None and log"""
    with patch("src.core.logger.StructuredLogger") as MockLogger:
        mock_logger_instance = MockLogger.return_value
        builder = build_regex.process_all_topics(product_topic, logger=mock_logger_instance)  # type: ignore

        assert builder is None
        mock_logger_instance.error.assert_called_once()

@pytest.mark.parametrize(argnames="known_topics", argvalues=[["gPu"], ["  MECHANICAL KEYBOARD  "]])
def test_build_from_topics_returns_detector_for_known_topic(known_topics: list[str]) -> None:
    detectors = build_regex.process_all_topics(known_topics)

    assert len(detectors) == 1
    assert detectors[0] is not None