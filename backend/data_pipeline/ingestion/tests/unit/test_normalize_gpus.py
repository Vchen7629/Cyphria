from src.products.computing.gpu.normalizer import GPUNameNormalizer
import pytest

def test_remove_duplicate_gpu_name() -> None:
    """Duplicate gpu names with different formats should be returned as the one normalized version"""
    detected_products = ["rtx 4090", "4090"]

    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == ["NVIDIA RTX 4090"]

@pytest.mark.parametrize(argnames="detected_products", argvalues=[
    ["rtx4090"], ["RtX 4090", "rtx 4090"], ["4090fe"], ["  rtx 4090  ", "rtx   4090"]
])
def test_normalizes_no_spaces_gpu_name(detected_products: list[str]) -> None:
    """GPU names should be properly normalized"""
    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == ["NVIDIA RTX 4090"]

@pytest.mark.parametrize(argnames="detected_products", argvalues=[
    [], ["Banana", "12345", "Intel 14700k", "idk"], ["9999"]
])
def test_invalid_products(detected_products: list[str]) -> None:
    """Empty input should return empty list"""
    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == []

def test_mixed_valid_and_invalid() -> None:
    """Valid GPUs should be normalized while invalid ones are filtered out"""
    detected_products = ["rtx 4090", "Intel 14700k", "7900 xtx", "doggo"]

    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == ["AMD RX 7900 XTX", "NVIDIA RTX 4090"]