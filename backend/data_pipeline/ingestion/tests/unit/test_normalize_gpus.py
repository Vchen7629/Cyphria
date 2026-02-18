from src.products.computing.gpu.normalizer import GPUNameNormalizer


def test_remove_duplicate_gpu_name() -> None:
    """Duplicate gpu names with different formats should be returned as the one normalized version"""
    detected_products = ["rtx 4090", "4090"]

    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == ["NVIDIA RTX 4090"]


def test_normalizes_no_spaces_gpu_name() -> None:
    """GPU names with no spaces should be properly normalized"""
    detected_products = ["rtx4090ti"]

    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == ["NVIDIA RTX 4090 Ti"]


def test_normalizes_case_insensitive_gpu_name() -> None:
    """GPU names with mixed cases should be properly normalized"""
    detected_products = ["RtX 4090", "rtx 4090"]

    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == ["NVIDIA RTX 4090"]


def test_founders_edition_gpu_normalized() -> None:
    """Test that it properly normalizes Founders edition (Fe)"""
    detected_products = ["3080fe"]

    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == ["NVIDIA RTX 3080"]


def test_empty_list() -> None:
    """Empty input should return empty list"""
    result = GPUNameNormalizer().normalize_gpu_list([])

    assert result == []


def test_all_invalid_gpu_names() -> None:
    """Invalid GPU names should be filtered out"""
    detected_products = ["Banana", "12345", "Intel 14700k", "idk"]

    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == []


def test_mixed_valid_and_invalid() -> None:
    """Valid GPUs should be normalized while invalid ones are filtered out"""
    detected_products = ["rtx 4090", "Intel 14700k", "7900 xtx", "doggo"]

    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == ["AMD RX 7900 XTX", "NVIDIA RTX 4090"]


def test_unknown_model_numbers() -> None:
    """Model numbers not in MODEL_TO_BRAND should be filtered out"""
    detected_products = ["9999"]

    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == []


def test_extra_whitespace() -> None:
    """Should handle extra whitespace"""
    detected_products = ["  rtx 4090  ", "rtx   4090"]

    result = GPUNameNormalizer().normalize_gpu_list(detected_products)

    assert result == ["NVIDIA RTX 4090"]
