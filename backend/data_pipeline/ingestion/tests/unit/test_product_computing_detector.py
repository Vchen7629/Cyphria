from typing import Optional
from src.products.computing.cpu.detector import CPUDetector
from src.products.computing.gpu.detector import GPUDetector
from src.products.computing.mechanical_keyboard.detector import MechanicalKeyboardDetector
import pytest

cpu_detector = CPUDetector()


@pytest.mark.parametrize(
    argnames="cpu_names",
    argvalues=[
        # Ryzen CPUs
        "MAX 395",
        "MAX+ 395",
        "Ryzen AI Max 395",
        "Ryzen AI Max+ 395",
        "Ryzen AI 9 475",
        "Ryzen AI 9 HX 475",
        "Ryzen 3900x3d",
        "3900x3d",
        "Ryzen 7 3900x3d",
        "Ryzen 7 3900",
        "Ryzen 3 PRO 1300",
        # Threadripper CPUs
        "Threadripper PRO 9995WX",
        "9995WX",
        "Threadripper 9980X",
        "Threadripper 9980X",
        ""
        # Intel cpus
        "i9-14900",
        "i9-14900K",
        "14900K",
        "265K",
        "Core Ultra 7 265K",
        "Core 5 120U",
        "i7-13700H",
        "13700H",
        "Pentium G620",
        "Pentium Gold G620",
        "G620",
    ],
)
def test_detects_cpus(cpu_names: str) -> None:
    assert cpu_detector.extract_cpus(cpu_names) == [cpu_names]
    assert cpu_detector.contains_cpu(cpu_names) is True


@pytest.mark.parametrize(
    argnames="cpu_names",
    argvalues=["No CPU", None, "", "I just bought the 3900", "I just bought the 9 475"],
)
def test_cpu_invalid_matches(cpu_names: Optional[str]) -> None:
    assert cpu_detector.extract_cpus(cpu_names) == []  # type: ignore
    assert cpu_detector.contains_cpu(cpu_names) is False  # type: ignore


@pytest.mark.parametrize(
    argnames="gpu_sentence,expected",
    argvalues=[
        ("I just bought the 4090, it's great!", ["4090"]),  # bare gpu number
        ("I just bought the rtx4070ti, it's great!", ["rtx4070ti"]),  # no spaces gpu name
        (
            "Should i buy the rtx 4090 or the rtx5090 for deep learning?",
            ["rtx 4090", "rtx5090"],
        ),  # multiple matches
        ("The 3090 Ti is very good.", ["3090 ti"]),  # gpu number with space between suffix
        ("my 3080fe/7700x starts to crumble on demanding games.", ["3080fe"]),  # matches fe
        (
            "I just bought a 4090 and my friend has a 4090",
            ["4090"],
        ),  # should deduplicate same gpu number
        (
            "i have a rtx 4090, RTX 3080, and RtX 2070",
            ["rtx 2070", "rtx 3080", "rtx 4090"],
        ),  # case insensitive
        (
            "I have [RTX 4090], its very nice",
            ["rtx 4090"],
        ),  # should still match with brackets around
    ],
)
def test_gpu_valid_matches(gpu_sentence: str, expected: list[str]) -> None:
    """Test if extract gpu function can match valid gpu strings"""
    assert GPUDetector().extract_gpus(gpu_sentence) == expected


@pytest.mark.parametrize(
    argnames="gpu_sentence", argvalues=["The price is 1234 dollars", "The sushi costs $4090"]
)
def test_gpu_invalid_matches(gpu_sentence: str) -> None:
    """Should not match invalid gpu sentences"""
    assert GPUDetector().extract_gpus(gpu_sentence) == []


def test_treats_different_formats_as_different() -> None:
    """Different format should match as different"""
    text = "The RTX 4090 is better than just the 4090"

    result = GPUDetector().extract_gpus(text)

    assert result == ["4090", "rtx 4090"]


@pytest.mark.parametrize(argnames="sentence,expected", argvalues=[
    # ai03 brand tests
    ("I just bought a new ai03 Altair-X", ["ai03 Altair-X"]), 
    ("I just bought a new Altair-X", ["Altair-X"]),
    ("Should i buy Vega or ai03 Vega?", ["ai03 Vega"]), # deduplicates
    # akko brand tests
    ("I have Akko Air 01, Akko Gem 01, Akko ACR59", ["Akko Air 01", "Akko Gem 01", "Akko ACR59"]),
    ("I have Mineral 01 and Akko Mineral 01", ["Akko Mineral 01"]), # deduplicates
    # Anne Pro brand tests
    ("I bought Anne Pro and Anne Pro 2 kbs", ["Anne Pro", "Anne Pro 2"]),
    # Asus ROG brand Test
    ("Should i buy the Strix Scope or Asus ROG Strix Scope NX", ["Strix Scope", "Asus ROG Strix Scope NX"]),
    ("New Azoth X, old Asus ROG Azoth X", ["Asus ROG Azoth X"]), # deduplicates
    # Corsair brand tests
    ("I have the k57, Corsair K60 Pro, and K70 Core", ["k57", "Corsair K60 Pro", "K70 Core"]),
    ("K100 and Corsair K100", ["Corsair K100"]), # deduplicates
])
def test_mechanical_keyboard_valid_matches(sentence: str, expected: list[str]) -> None:
    """Should correctly extract and detect mechanical keyboard names"""
    detector = MechanicalKeyboardDetector()
    assert detector.extract_mechanical_keyboards(sentence) == sorted(expected)
    assert detector.contains_mechanical_keyboard(sentence) is True

@pytest.mark.parametrize(argnames="sentence", argvalues=[
    "The price is 1234 dollars", "The sushi costs $4090", None, 23332]
)
def test_mechanical_keyboard_invalid_matches(sentence: str) -> None:
    """Should not match invalid gpu sentences"""
    detector = MechanicalKeyboardDetector()
    assert detector.extract_mechanical_keyboards(sentence) == []
    assert detector.contains_mechanical_keyboard(sentence) is False

