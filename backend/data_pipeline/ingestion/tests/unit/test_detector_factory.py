from src.product_utils.detector_factory import DetectorFactory
import pytest

def test_unsupported_category() -> None:
    """Unsupported method should raise value error"""
    with pytest.raises(
        ValueError, 
        match="Unsupported category: 'GPUsd'. Supported: gpu"
    ):
        factory = DetectorFactory.get_detector("GPUsd")
        factory.extract_products("hello world")

def test_supported_category_extract_products() -> None:
    """Supported category should return a list of product names"""
    factory = DetectorFactory.get_detector("GPU")

    res = factory.extract_products("i have RTX 4090, i want RTX 5090")

    assert res == ["rtx 4090", "rtx 5090"]

def test_supported_category_contains_product() -> None:
    """Supported category should return a boolean"""
    factory = DetectorFactory.get_detector("GPU")

    res = factory.contains_product("i have RTX 4090, i want RTX 5090")

    assert res

def test_category_case_insensitivity() -> None:
    """Mixed case should still match"""
    factory = DetectorFactory.get_detector("GpU")

    res = factory.contains_product("i have RTX 4090")

    assert res

def test_white_space_category() -> None:
    """White space should still match"""
    factory = DetectorFactory.get_detector("  GPU  ")

    res = factory.contains_product("i have RTX 4090")

    assert res