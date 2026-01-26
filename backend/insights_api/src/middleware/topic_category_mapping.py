
from typing import Optional
TOPIC_TO_CATEGORY: dict[str, str] = {
    # Audio
    "DAC": "Audio",
    "EARBUD": "Audio",
    "HEADPHONE": "Audio",
    "SOUNDBAR": "Audio",
    # Computing
    "CPU": "Computing",
    "GPU": "Computing",
    "LAPTOP": "Computing",
    "MECHANICAL KEYBOARD": "Computing",
    "MONITOR": "Computing",
    # Gaming
    "CONTROLLER": "Gaming",
    "GAMING HEADSET": "Gaming",
    "GAMING MICE": "Gaming",
    # Home
    "AIR PURIFIER": "Home",
    "HUMIDIFIER": "Home",
    "ROBOT VACUUM": "Home",
    # Mobile
    "SMARTPHONE": "Mobile",
    "TABLET": "Mobile",
    # Photography
    "CAMERA": "Photography",
    "LENSE": "Photography",
    "TRIPOD": "Photography",
    # Wearables
    "SMARTWATCH": "Wearable",
    "WATCH": "Wearable"
}

CATEGORY_TO_TOPICS: dict[str, list[str]] = {
    "audio": ["dac", "earbud", "headphone", "soundbar"],
    "computing": ["cpu", "gpu", "laptop", "mechanical keyboard", "monitor"],
    "gaming": ["controller", "gaming headset", "gaming mice"],
    "home": ["air purifier", "humidifier", "robot vacuum"],
    "mobile": ["smartphone", "tablet"],
    "photography": ["camera", "lense", "tripod"],
    "wearable": ["smartwatch", "watch"]
}

def get_category_for_topic(product_topic: str) -> Optional[str]:
    """
    Get the category name for a give product_topic

    Args:
        product_topic: the topic name, like "GPU", "Laptop"

    Returns:
        Category name or None if product_topic not found
    """
    if not product_topic:
        return None

    return TOPIC_TO_CATEGORY.get(product_topic.strip().upper())

def get_topics_for_category(category: str) -> list[str]:
    """
    Get all product_topics belonging to a category

    Args:
        category: the category name like "Computing"

    Returns:
        list of product_topic names, like ["GPU", "Laptop"] or empty list if not found
    """
    if not category:
        return []

    return CATEGORY_TO_TOPICS.get(category.strip().lower(), [])