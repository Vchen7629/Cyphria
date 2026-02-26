from src.product_detector.base import ProductDetector
from src.product_detector.base import BuildDetectorRegex
from src.product_mappings.computing import GPU_MODEL_TO_BRAND
from src.product_mappings.computing import CPU_MODEL_TO_BRAND
from src.product_mappings.computing import KEYBOARD_MODEL_TO_BRAND
from src.product_mappings.computing import MONITOR_MODEL_TO_BRAND
import pytest


@pytest.mark.parametrize(
    argnames="sentence,expected",
    argvalues=[
        # Ryzen CPUs
        (
            "I have a MAX 395, MAX+ 395, Ryzen AI 9 HX 475, and 3900x3d",
            ["MAX 395", "MAX+ 395", "Ryzen AI 9 HX 475", "3900x3d"],
        ),
        ("My 3900x3d broke, i bought a new Ryzen 3900x3d", ["Ryzen 3900x3d"]),
        ("The new thReadRipper PrO 9995WX is great", ["thReadRipper PrO 9995WX"]),
        # Intel cpus
        (
            "I have a i9-14900, i9-14900K, i7-13700H, and Core Ultra 7 265K",
            ["Core Ultra 7 265K", "i7-13700H", "i9-14900", "i9-14900K"],
        ),
        ("I have a Pentium G620 and my friend has Intel Pentium G620", ["Pentium G620"]),
    ],
)
def test_cpu_valid_matches(sentence: str, expected: list[str]) -> None:
    """Test if it can match valid CPU strings"""
    cpu_regex_pattern = BuildDetectorRegex().process_all_topics(["CPU"])[0]
    assert cpu_regex_pattern is not None
    detector = ProductDetector(pattern=cpu_regex_pattern, mapping=CPU_MODEL_TO_BRAND)
    assert detector.extract_products(sentence) == sorted(expected)
    assert detector.contains_product(sentence) is True


@pytest.mark.parametrize(
    argnames="sentence,expected",
    argvalues=[
        ("I just bought the 4090, it's great!", ["4090"]),  # bare gpu number
        ("I just bought the rtx4070ti, it's great!", ["rtx4070ti"]),  # no spaces gpu name
        (
            "Should i buy the rtx 4090 or the rtx5090 for deep learning?",
            ["rtx 4090", "rtx5090"],
        ),  # multiple matches
        ("The 3090 Ti is very good.", ["3090 Ti"]),  # gpu number with space between suffix
        ("my 3080fe/7700x starts to crumble on demanding games.", ["3080fe"]),  # matches fe
        (
            "I just bought a 4090 and my friend has a RTX 4090",
            ["RTX 4090"],
        ),  # should deduplicate same gpu number
        (
            "i have a rtx 4090, RTX 3080, and RtX 2070",
            ["RtX 2070", "RTX 3080", "rtx 4090"],
        ),  # case insensitive
        (
            "I have [RTX 4090], its very nice",
            ["RTX 4090"],
        ),  # should still match with brackets around
    ],
)
def test_gpu_valid_matches(sentence: str, expected: list[str]) -> None:
    """Test if extract gpu function can match valid gpu strings"""
    gpu_regex_pattern = BuildDetectorRegex().process_all_topics(["GPU"])[0]
    assert gpu_regex_pattern is not None
    detector = ProductDetector(pattern=gpu_regex_pattern, mapping=GPU_MODEL_TO_BRAND)
    assert detector.extract_products(sentence) == sorted(expected)
    assert detector.contains_product(sentence) is True


@pytest.mark.parametrize(
    argnames="sentence,expected",
    argvalues=[
        # ai03 brand tests
        ("I just bought a new ai03 Altair-X", ["ai03 Altair-X"]),
        ("I just bought a new Altair-X", ["Altair-X"]),
        ("Should i buy Vega or ai03 Vega?", ["ai03 Vega"]),  # deduplicates
        # akko brand tests
        (
            "I have Akko Air 01, Akko Gem 01, Akko ACR59",
            ["Akko Air 01", "Akko Gem 01", "Akko ACR59"],
        ),
        ("I have Mineral 01 and Akko Mineral 01", ["Akko Mineral 01"]),  # deduplicates
        # Anne Pro brand tests
        ("I bought Anne Pro and Anne Pro 2 kbs", ["Anne Pro", "Anne Pro 2"]),
        # Asus ROG brand Test
        (
            "Should i buy the Strix Scope or Asus ROG Strix Scope NX",
            ["Strix Scope", "Asus ROG Strix Scope NX"],
        ),
        ("New Azoth X, old Asus ROG Azoth X", ["Asus ROG Azoth X"]),  # deduplicates
        # Corsair brand tests
        ("I have the k57, Corsair K60 Pro, and K70 Core", ["k57", "Corsair K60 Pro", "K70 Core"]),
        ("K100 and Corsair K100", ["Corsair K100"]),  # deduplicates
    ],
)
def test_mechanical_keyboard_valid_matches(sentence: str, expected: list[str]) -> None:
    """Should correctly extract and detect mechanical keyboard names"""
    keyboard_regex_pattern = BuildDetectorRegex().process_all_topics(["MECHANICAL KEYBOARD"])[0]
    assert keyboard_regex_pattern is not None
    detector = ProductDetector(pattern=keyboard_regex_pattern, mapping=KEYBOARD_MODEL_TO_BRAND)
    assert detector.extract_products(sentence) == sorted(expected)
    assert detector.contains_product(sentence) is True


@pytest.mark.parametrize(
    argnames="sentence,expected",
    argvalues=[
        ("I just bought a new BL0 to complement my Odyssey g9", ["BL0", "Odyssey g9"]),
        ("I have a Samsung Odyssey g9 and my friend has a Odyssey g9", ["Samsung Odyssey g9"]),
    ],
)
def test_monitor_valid_matches(sentence: str, expected: list[str]) -> None:
    """Should correctly extract and detect monitor names"""
    monitor_regex_pattern = BuildDetectorRegex().process_all_topics(["Monitor"])[0]
    assert monitor_regex_pattern is not None
    detector = ProductDetector(pattern=monitor_regex_pattern, mapping=MONITOR_MODEL_TO_BRAND)
    assert detector.extract_products(sentence) == sorted(expected)
    assert detector.contains_product(sentence) is True


@pytest.mark.parametrize(
    argnames="sentence,expected_by_topic",
    argvalues=[
        (
            "I have a MAX 395, rtx3080, ai03 Altair-X, and Odyssey g9",
            {
                "CPU": ["MAX 395"],
                "GPU": ["rtx3080"],
                "MECHANICAL KEYBOARD": ["ai03 Altair-X"],
                "MONITOR": ["Odyssey g9"],
            },
        ),
        (
            "My 3900x3d and rtx 4090 are great for gaming",
            {
                "CPU": ["3900x3d"],
                "GPU": ["rtx 4090"],
                "MECHANICAL KEYBOARD": [],
                "MONITOR": [],
            },
        ),
    ],
)
def test_multiple_topics_valid_matches(
    sentence: str, expected_by_topic: dict[str, list[str]]
) -> None:
    """Test that each topic detector extracts only its relevant products"""
    topics = ["CPU", "GPU", "MECHANICAL KEYBOARD", "MONITOR"]
    mappings = {
        "CPU": CPU_MODEL_TO_BRAND,
        "GPU": GPU_MODEL_TO_BRAND,
        "MECHANICAL KEYBOARD": KEYBOARD_MODEL_TO_BRAND,
        "MONITOR": MONITOR_MODEL_TO_BRAND,
    }

    regex_patterns = BuildDetectorRegex().process_all_topics(topics)
    assert regex_patterns is not None
    assert len(regex_patterns) == len(topics)

    for topic, pattern in zip(topics, regex_patterns):
        detector = ProductDetector(pattern=pattern, mapping=mappings[topic])  # type: ignore
        expected = expected_by_topic[topic]

        if expected:
            assert detector.extract_products(sentence) == sorted(expected)
            assert detector.contains_product(sentence) is True
        else:
            assert detector.extract_products(sentence) == []
            assert detector.contains_product(sentence) is False


@pytest.mark.parametrize(
    argnames="sentence",
    argvalues=["The price is 1234 dollars", "The sushi costs $4090", None, 23332],
)
def test_invalid_matches(sentence: str) -> None:
    """Should not match invalid gpu sentences"""
    keyboard_regex_pattern = BuildDetectorRegex().process_all_topics(["Monitor"])[0]
    assert keyboard_regex_pattern is not None
    detector = ProductDetector(pattern=keyboard_regex_pattern, mapping=KEYBOARD_MODEL_TO_BRAND)
    assert detector.extract_products(sentence) == []
    assert detector.contains_product(sentence) is False
