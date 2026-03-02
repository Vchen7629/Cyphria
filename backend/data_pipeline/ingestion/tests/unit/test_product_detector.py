from src.product_detector.base import ProductDetector
from src.product_detector.base import BuildDetectorRegex
from src.product_mappings.computing import GPU_MODEL_TO_BRAND
from src.product_mappings.computing import CPU_MODEL_TO_BRAND
from src.product_mappings.computing import LAPTOP_MODEL_TO_BRAND
from src.product_mappings.computing import KEYBOARD_MODEL_TO_BRAND
from src.product_mappings.computing import MONITOR_MODEL_TO_BRAND
from src.product_mappings.audio import DAC_MODEL_TO_BRAND
from src.product_mappings.audio import EARBUD_MODEL_TO_BRAND
from src.product_mappings.audio import SPEAKER_MODEL_TO_BRAND
from src.product_mappings.audio import SOUNDBAR_MODEL_TO_BRAND
from src.product_mappings.audio import HEADPHONE_MODEL_TO_BRAND
import pytest


@pytest.mark.parametrize(
    argnames="sentence,expected,topic,mapping",
    argvalues=[
        # multiple matches
        (
            "I have a MAX 395, MAX+ 395, Ryzen AI 9 HX 475, and 3900x3d",
            ["MAX 395", "MAX+ 395", "Ryzen AI 9 HX 475", "3900x3d"],
            "CPU",
            CPU_MODEL_TO_BRAND,
        ),
        (
            "Should i buy the rtx 4090 or the rtx5090 for deep learning?",
            ["rtx 4090", "rtx5090"],
            "GPU",
            GPU_MODEL_TO_BRAND,
        ),
        (
            "I have Akko Air 01, Akko Gem 01, Akko ACR59",
            ["Akko Air 01", "Akko Gem 01", "Akko ACR59"],
            "MECHANICAL KEYBOARD",
            KEYBOARD_MODEL_TO_BRAND,
        ),
        (
            "I just bought a new BL0 to complement my Odyssey g9",
            ["BL0", "Odyssey g9"],
            "MONITOR",
            MONITOR_MODEL_TO_BRAND,
        ),
        (
            "I have a Nitro V 15, Aero 5, and Lenovo IdeaPad 1",
            ["Nitro V 15", "Aero 5", "Lenovo IdeaPad 1"],
            "LAPTOP",
            LAPTOP_MODEL_TO_BRAND,
        ),
        (
            "I have a K72, Apple Airpods Max, and WH-CH520",
            ["K72", "Apple Airpods Max", "WH-CH520"],
            "HEADPHONE",
            HEADPHONE_MODEL_TO_BRAND,
        ),
        (
            "I have a ATH-CKS50TW2, Apple Airpods 4, and Live Flex 3",
            ["ATH-CKS50TW2", "Apple Airpods 4", "Live Flex 3"],
            "EARBUD",
            EARBUD_MODEL_TO_BRAND,
        ),
        (
            "I have a Bose 550, LG H7, and B400F",
            ["Bose 550", "LG H7", "B400F"],
            "SOUNDBAR",
            SOUNDBAR_MODEL_TO_BRAND,
        ),
        (
            "I have a DragonFly Black, Gustard R26, and Erco",
            ["DragonFly Black", "Gustard R26", "Erco"],
            "DAC",
            DAC_MODEL_TO_BRAND,
        ),
        (
            "I have a Echo Dot, Elac Concertro, and Aria SR900",
            ["Echo Dot", "Elac Concertro", "Aria SR900"],
            "SPEAKER",
            SPEAKER_MODEL_TO_BRAND,
        ),
        # deduplicate
        (
            "I just bought a 4090 and my friend has a RTX 4090",
            ["RTX 4090"],
            "GPU",
            GPU_MODEL_TO_BRAND,
        ),
        (
            "I have a Pentium G620 and my friend has Intel Pentium G620",
            ["Pentium G620"],
            "CPU",
            CPU_MODEL_TO_BRAND,
        ),
        ("K100 and Corsair K100", ["Corsair K100"], "MECHANICAL KEYBOARD", KEYBOARD_MODEL_TO_BRAND),
        (
            "I have a Samsung Odyssey g9 and my friend has a Odyssey g9",
            ["Samsung Odyssey g9"],
            "MONITOR",
            MONITOR_MODEL_TO_BRAND,
        ),
        (
            "i have Aero 5, he has Gigabyte Aero 5",
            ["Gigabyte Aero 5"],
            "LAPTOP",
            LAPTOP_MODEL_TO_BRAND,
        ),
        (
            "my old WH-CH520 broke, i bought a new Sony WH-CH520",
            ["Sony WH-CH520"],
            "HEADPHONE",
            HEADPHONE_MODEL_TO_BRAND,
        ),
        (
            "my old Airpods 4 broke, i bought a new Apple Airpods 4",
            ["Apple Airpods 4"],
            "EARBUD",
            EARBUD_MODEL_TO_BRAND,
        ),
        (
            "my old B400F broke, i bought a new Samsung HW-B400F",
            ["Samsung HW-B400F"],
            "SOUNDBAR",
            SOUNDBAR_MODEL_TO_BRAND,
        ),
        (
            "my old DM7 broke, i bought a new Topping DM7",
            ["Topping DM7"],
            "DAC",
            DAC_MODEL_TO_BRAND,
        ),
        (
            "my old Echo Dot broke, i bought a new Amazon Echo Dot",
            ["Amazon Echo Dot"],
            "SPEAKER",
            SPEAKER_MODEL_TO_BRAND,
        ),
    ],
)
def test_product_topic_valid_matches(
    sentence: str, expected: list[str], topic: str, mapping: dict[str, str]
) -> None:
    """Test if it can match valid topic strings"""
    product_regex_pattern = BuildDetectorRegex().process_all_topics([topic])[0]
    assert product_regex_pattern is not None
    detector = ProductDetector(pattern=product_regex_pattern, mapping=mapping)
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
