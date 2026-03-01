from typing import Optional
from unittest.mock import patch
from src.product_normalizer.base import ProductNormalizer
import pytest


@pytest.mark.parametrize(
    argnames="cpu_names,expected_name",
    argvalues=[
        # intel cpus
        (["3930K", "Core 3930K", "Core i7-3930K", "i7-3930K"], "Intel Core i7-3930K"),
        (["G5500T", "Pentium G5500T", "Pentium Gold G5500T"], "Intel Pentium Gold G5500T"),
        (["G4900T", "Celeron G4900T"], "Intel Celeron G4900T"),
        (
            [
                "7740X",
                "Core 7740X",
                "i7-7740X",
                "i7 X i7-7740X",
                "Core i7-7740X",
                "Core i7 X i7-7740X",
            ],
            "Intel Core i7 X i7-7740X",
        ),
        (["235T", "Core Ultra 235T", "Core Ultra 5 235T"], "Intel Core Ultra 5 235T"),
        # ryzen cpus
        (["5500X3D", "Ryzen 5500X3D", "Ryzen 5 5500X3D"], "AMD Ryzen 5 5500X3D"),
        (
            ["7995WX", "Ryzen 7995WX", "Ryzen Threadripper Pro 7995WX", "Threadripper Pro 7995WX"],
            "AMD Ryzen Threadripper Pro 7995WX",
        ),
    ],
)
def test_cpu_normalized(cpu_names: list[str], expected_name: str) -> None:
    """Should normalize intel cpus properly"""
    normalizer = ProductNormalizer()
    config = ProductNormalizer._TOPIC_CONFIGS["CPU"]
    mapping, custom_norm = config
    for name in cpu_names:
        result = normalizer.normalize_product_list("CPU", [name])
        assert result == [expected_name]


@pytest.mark.parametrize(
    argnames="gpu_list,expected",
    argvalues=[
        (
            ["rtx 4090", "4090"],
            ["NVIDIA RTX 4090"],
        ),  # should deduplicate
        (["rtx3060"], ["NVIDIA RTX 3060"]),  # no spaces
        (["1030"], ["NVIDIA GT 1030"]),
        (["  4090  "], ["NVIDIA RTX 4090"]),
        (["3070ti"], ["NVIDIA RTX 3070 Ti"]),
    ],
)
def test_gpu_normalized(gpu_list: list[str], expected: list[str]) -> None:
    """GPUs should be properly normalized"""
    normalized = ProductNormalizer().normalize_product_list("GPU", gpu_list)
    assert normalized == sorted(expected)


@pytest.mark.parametrize(
    argnames="keyboard_list,expected",
    argvalues=[
        (["Altair-X", "Vega", "ai03 Vega"], ["ai03 Altair-X", "ai03 Vega"]),  # should deduplicate
        (
            ["   Air 01  ", "gEm 01"],
            ["Akko Air 01", "Akko Gem 01"],
        ),  # should handle whitespace + mixed case
        (
            ["jajaja", "Altair-X", "Air 01"],
            ["ai03 Altair-X", "Akko Air 01"],
        ),  # should filter out invalid keyboard
    ],
)
def test_mechanical_keyboard_normalized(keyboard_list: list[str], expected: list[str]) -> None:
    """Should normalize valid mechanical keyboard names"""
    normalized = ProductNormalizer().normalize_product_list("MECHANICAL KEYBOARD", keyboard_list)
    assert normalized == sorted(expected)


@pytest.mark.parametrize(
    argnames="keyboard_list,expected",
    argvalues=[
        (
            ["BE0", "Acer BE0", "XG27ACDMS"],
            ["Acer BE0", "Asus ROG Strix OLED XG27ACDMS"],
        ),  # should deduplicate
        (
            ["   EX240  ", "Ex271uZ"],
            ["BenQ Mobiuz EX240", "BenQ Mobiuz OLED EX271UZ"],
        ),  # should handle whitespace + mixed case
        (
            ["jajaja", "BE0"],
            ["Acer BE0"],
        ),  # should filter out invalid keyboard
    ],
)
def test_monitor_normalized(keyboard_list: list[str], expected: list[str]) -> None:
    """Should normalize valid monitor names"""
    normalized = ProductNormalizer().normalize_product_list("MONITOR", keyboard_list)
    assert normalized == sorted(expected)


@pytest.mark.parametrize(
    argnames="laptop_list,expected",
    argvalues=[
        (["Aero 5", "Omen Max", "LG gram 14"], ["Gigabyte Aero 5", "HP Omen Max", "LG gram 14"]),
        (["Aero 5", "Gigabyte Aero 5"], ["Gigabyte Aero 5"]),  # deduplicate
    ],
)
def test_laptop_normalized(laptop_list: list[str], expected: list[str]) -> None:
    """Laptops should be properly normalized"""
    normalized = ProductNormalizer().normalize_product_list("LAPTOP", laptop_list)
    assert normalized == sorted(expected)


@pytest.mark.parametrize(argnames="product_topic", argvalues=[None, "", "  "])
def test_invalid_input_product_topic(product_topic: str | None) -> None:
    """Invalid product topic param (None, empty string, whitespace) should return None and log"""
    with patch("shared_core.logger.StructuredLogger") as MockLogger:
        mock_logger_instance = MockLogger.return_value
        normalizer = ProductNormalizer(mock_logger_instance).normalize_product_list(
            product_topic,  # type: ignore
            product_list=["hi"],
        )

        assert normalizer == []
        mock_logger_instance.error.assert_called_once()


@pytest.mark.parametrize(
    argnames="cpu_list", argvalues=[None, [], ["Banana", "12345", "idk"], ["9999"]]
)
def test_invalid_cpu_input(cpu_list: Optional[list[str]]) -> None:
    """CPUNormalizer shouldnt normalize invalid cpu strings"""
    assert ProductNormalizer().normalize_product_list("cpu", cpu_list) == []  # type: ignore


@pytest.mark.parametrize(
    argnames="topic,product_list",
    argvalues=[
        ("GPU", ["RTX 4090", "RTX 5090"]),
        ("GpU", ["RTX 4090", "RTX 5090"]),
        ("  GPU  ", ["RTX 4090", "RTX 5090"]),
    ],
)
def test_valid_category_normalize(topic: str, product_list: list[str]) -> None:
    """Supported category should properly normalize product names"""
    res = ProductNormalizer().normalize_product_list(topic, product_list)

    assert res == ["NVIDIA RTX 4090", "NVIDIA RTX 5090"]
