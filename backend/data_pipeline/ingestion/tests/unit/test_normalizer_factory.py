from src.product_utils.normalizer_factory import NormalizerFactory
import pytest

def test_unsupported_category() -> None:
    """Unsupported method should raise value error"""
    with pytest.raises(
        ValueError, 
        match="Unsupported category: 'GPUsd'. Supported: gpu"
    ):
        NormalizerFactory.normalize("GPUsd", ["RTX 3090"])

def test_supported_category_normalize() -> None:
    """Supported category should properly normalize product names"""
    res = NormalizerFactory.normalize("GPU", ["RTX 4090", "RTX 5090"])

    assert res == ["NVIDIA RTX 4090", "NVIDIA RTX 5090"]

def test_category_case_insensitivity() -> None:
    """Mixed case should still match"""
    res = NormalizerFactory.normalize("GpU", ["RTX 4090", "RTX 5090"])

    assert res == ["NVIDIA RTX 4090", "NVIDIA RTX 5090"]

def test_white_space_category() -> None:
    """White space should still match"""
    res = NormalizerFactory.normalize("  GPU  ", ["RTX 4090", "RTX 5090"])

    assert res == ["NVIDIA RTX 4090", "NVIDIA RTX 5090"]
