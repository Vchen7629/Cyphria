from unittest.mock import patch
from src.product_utils.detector_factory import DetectorFactory
import pytest

@pytest.mark.parametrize(argnames="product_topic", argvalues=[None, "", "  "])
def test_invalid_input_product_topic(product_topic: str | None) -> None:
    """Invalid product topic param (None, empty string, whitespace) should return None and log"""
    with patch("src.core.logger.StructuredLogger") as MockLogger:
        mock_logger_instance = MockLogger.return_value
        factory = DetectorFactory.get_detector(product_topic, logger=mock_logger_instance) # type: ignore

        assert factory is None
        mock_logger_instance.error.assert_called_once()

def test_unsupported_product_topic() -> None:
    """Unsupported method should raise value error"""
    with pytest.raises(
        ValueError, 
        match="Unsupported product_topic: 'GPUsd'. Supported: gpu"
    ):
        factory = DetectorFactory.get_detector("GPUsd")
        assert factory is not None
        factory.extract_products("hello world")

def test_supported_product_topic_extract_products() -> None:
    """Supported product_topic should return a list of product names"""
    factory = DetectorFactory.get_detector("GPU")
    assert factory is not None
    res = factory.extract_products("i have RTX 4090, i want RTX 5090")

    assert res == ["rtx 4090", "rtx 5090"]

def test_supported_product_topic_contains_product() -> None:
    """Supported product_topic should return a boolean"""
    factory = DetectorFactory.get_detector("GPU")
    assert factory is not None

    res = factory.contains_product("i have RTX 4090, i want RTX 5090")

    assert res

def test_product_topic_case_insensitivity() -> None:
    """Mixed case should still match"""
    factory = DetectorFactory.get_detector("GpU")
    assert factory is not None

    res = factory.contains_product("i have RTX 4090")

    assert res

def test_white_space_product_topic() -> None:
    """White space should still match"""
    factory = DetectorFactory.get_detector("  GPU  ")
    assert factory is not None

    res = factory.contains_product("i have RTX 4090")

    assert res