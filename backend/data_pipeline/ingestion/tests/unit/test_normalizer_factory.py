from unittest.mock import patch
from src.products.normalizer_factory import NormalizerFactory
import pytest


@pytest.mark.parametrize(argnames="product_topic", argvalues=[None, "", "  "])
def test_invalid_input_product_topic(product_topic: str | None) -> None:
    """Invalid product topic param (None, empty string, whitespace) should return None and log"""
    with patch("src.core.logger.StructuredLogger") as MockLogger:
        mock_logger_instance = MockLogger.return_value
        factory = NormalizerFactory.normalize(
            product_topic,  # type: ignore
            product_list=["hi"],
            logger=mock_logger_instance,
        )

        assert factory is None
        mock_logger_instance.error.assert_called_once()


def test_unsupported_category() -> None:
    """Unsupported method should raise value error"""
    with pytest.raises(ValueError, match="Unsupported product_topic: 'GPUsd'. Supported: gpu"):
        NormalizerFactory.normalize("GPUsd", ["RTX 3090"])

@pytest.mark.parametrize(argnames="category,product_list", argvalues=[
    ("GPU", ["RTX 4090", "RTX 5090"]), ("GpU", ["RTX 4090", "RTX 5090"]), ("  GPU  ", ["RTX 4090", "RTX 5090"])
])
def test_valid_category_normalize(category: str, product_list: list[str]) -> None:
    """Supported category should properly normalize product names"""
    res = NormalizerFactory.normalize(category, product_list)

    assert res == ["NVIDIA RTX 4090", "NVIDIA RTX 5090"]