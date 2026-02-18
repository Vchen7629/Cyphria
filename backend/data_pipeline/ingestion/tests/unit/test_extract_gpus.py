from src.products.computing.gpu.detector import GPUDetector


def test_matches_bare_gpu_number() -> None:
    """Test if extract gpu function can detect a bare gpu number like 4090"""
    text = "I just bought the 4090, it's great!"

    result = GPUDetector().extract_gpus(text)

    assert result == ["4090"]


def test_matches_no_spaces_gpu_name() -> None:
    """Test that it matches a gpu name with no spaces like rtx4070ti"""
    text = "I just bought the rtx4070ti, it's great!"

    result = GPUDetector().extract_gpus(text)

    assert result == ["rtx4070ti"]


def test_matches_multiple_gpu_names() -> None:
    """Test that it matches multiple gpu names in a comment"""
    text = "Should i buy the rtx 4090 or the rtx5090 for deep learning?"

    result = GPUDetector().extract_gpus(text)

    assert result == ["rtx 4090", "rtx5090"]


def test_matches_bare_gpu_number_with_ti() -> None:
    """Should match bare numbers with Ti suffix"""
    text = "The 3090 Ti is very good."

    result = GPUDetector().extract_gpus(text)

    assert result == ["3090 ti"]


def test_matches_bare_gpu_number_with_fe() -> None:
    """Should match bare numbers with Fe (Founders edition) suffix"""
    text = "And i sit here playing some games that are a bit demanding and my 3080fe/7700x starts to crumble."

    result = GPUDetector().extract_gpus(text)

    assert result == ["3080fe"]


def test_ignores_unknown_numbers() -> None:
    """Should not match random 4-digit rumbers"""
    text = "The price is 1234 dollars"

    result = GPUDetector().extract_gpus(text)

    assert result == []


def test_ignores_prices_with_dollar_sign() -> None:
    """Should not match numbers that match a gpu number but have dollar sign"""
    text = "The sushi costs $4090"

    result = GPUDetector().extract_gpus(text)

    assert result == []


def test_deduplicates_same_gpu() -> None:
    """Should return each unique GPU only once"""
    text = "I just bought a 4090 and my friend has a 4090"

    result = GPUDetector().extract_gpus(text)

    assert result == ["4090"]


def test_treats_different_formats_as_different() -> None:
    """Different format should match as different"""
    text = "The RTX 4090 is better than just the 4090"

    result = GPUDetector().extract_gpus(text)

    assert result == ["4090", "rtx 4090"]


def test_case_insensitive_matching() -> None:
    """Should match regardless of case"""
    text = "i have a rtx 4090, RTX 3080, and RtX 2070"

    result = GPUDetector().extract_gpus(text)

    assert result == ["rtx 2070", "rtx 3080", "rtx 4090"]


def test_match_gpu_with_brackets() -> None:
    """Should match GPU name surrounded by punctuation"""
    text = "I have [RTX 4090], its very nice"

    result = GPUDetector().extract_gpus(text)

    assert result == ["rtx 4090"]
