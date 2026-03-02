from typing import Optional
from unittest.mock import patch
from src.product_normalizer.base import ProductNormalizer
import pytest

normalizer = ProductNormalizer()


@pytest.mark.parametrize(
    argnames="product_list,expected,topic",
    argvalues=[
        # multiple matches
        (["  4090  ", "RTX 5090"], ["NVIDIA RTX 4090", "NVIDIA RTX 5090"], "GPU"),
        (["   Air 01  ", "gEm 01"], ["Akko Air 01", "Akko Gem 01"], "MECHANICAL KEYBOARD"),
        (["   EX240  ", "Ex271uZ"], ["BenQ Mobiuz EX240", "BenQ Mobiuz OLED EX271UZ"], "MONITOR"),
        (
            ["Aero 5", "Omen Max", "LG gram 14"],
            ["Gigabyte Aero 5", "HP Omen Max", "LG gram 14"],
            "LAPTOP",
        ),
        (
            ["K72", "Apple Airpods Max", "WH-CH520"],
            ["AKG K72", "Apple Airpods Max", "Sony WH-CH520"],
            "HEADPHONE",
        ),
        (
            ["Ambeo Max", "H7", "B400F"],
            ["Sennheiser Ambeo Max", "LG H7", "Samsung HW-B400F"],
            "SOUNDBAR",
        ),
        (
            ["DragonFly Black", "Gustard R26", "Erco"],
            ["AudioQuest DragonFly Black", "Gustard R26", "Ferrum Erco"],
            "DAC",
        ),
        (
            ["ATH-CKS50TW2", "Apple Airpods 4", "Live Flex 3"],
            ["Audio-Technica ATH-CKS50TW2", "Apple Airpods 4", "JBL Live Flex 3"],
            "EARBUD",
        ),
        (
            ["Echo Dot", "Elac Concertro", "Aria SR900"],
            ["Amazon Echo Dot", "Elac Concertro", "Focal Aria SR900"],
            "SPEAKER",
        ),
        # deduplicates
        (["3930K", "Core i7-3930K", "i7-3930K"], ["Intel Core i7-3930K"], "CPU"),
        (["rtx 4090", "4090"], ["NVIDIA RTX 4090"], "GPU"),
        (["Vega", "ai03 Vega"], ["ai03 Vega"], "MECHANICAL KEYBOARD"),
        (["BE0", "Acer BE0"], ["Acer BE0"], "MONITOR"),
        (["Aero 5", "Gigabyte Aero 5"], ["Gigabyte Aero 5"], "LAPTOP"),
        (["WH-CH520", "Sony WH-CH520"], ["Sony WH-CH520"], "HEADPHONE"),
        (["B400F", "Samsung HW-B400F"], ["Samsung HW-B400F"], "SOUNDBAR"),
        (["DM7", "Topping DM7"], ["Topping DM7"], "DAC"),
        (["Airpods 4", "Apple Airpods 4"], ["Apple Airpods 4"], "EARBUD"),
        (["Echo Dot", "Amazon Echo Dot"], ["Amazon Echo Dot"], "SPEAKER"),
    ],
)
def test_product_normalized(product_list: list[str], expected: list[str], topic: str) -> None:
    """products should be properly normalized"""
    normalized = normalizer.normalize_product_list(topic, product_list)
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
    assert normalizer.normalize_product_list("cpu", cpu_list) == []  # type: ignore


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
    res = normalizer.normalize_product_list(topic, product_list)

    assert res == ["NVIDIA RTX 4090", "NVIDIA RTX 5090"]
