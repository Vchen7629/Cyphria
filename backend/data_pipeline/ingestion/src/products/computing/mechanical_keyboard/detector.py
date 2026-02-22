from collections import defaultdict
import re
from src.products.computing.mechanical_keyboard.mappings import KEYBOARD_MODEL_TO_BRAND


class MechanicalKeyboardDetector:
    """Detects Mechanical Keyboard product mentions in comments"""

    def extract_mechanical_keyboards(self, text: str) -> list[str]:
        """
        Extract all mechanical keyboards mentions from the text

        Args:
            text: comment text that we are checking

        Returns:
            list: list of all matching mechanical keyboard name strings or empty list if no mechanical keyboards
        """
        if not text or not isinstance(text, str):
            return []

        detected_products = self._detect_products(text)

        deduplicated_products = self._deduplicate(detected_products)

        return sorted(list(deduplicated_products))

    def contains_mechanical_keyboard(self, text: str) -> bool:
        """
        Check if comment text contains any mechanical keyboard mention

        Args:
            text: comment text string we're checking for

        Returns:
            bool: true if there is at least one mention of mechanical
                false otherwise
        """
        if not text or not isinstance(text, str):
            return False

        return bool(self._detect_products(text))

    def _build_pattern() -> re.Pattern[str]:
        """Builds compiled regex from mapping, grouping models by brand"""
        brand_groups = defaultdict(list)
        for model, brand in KEYBOARD_MODEL_TO_BRAND.items():
            brand_groups[brand].append(model)

        parts: list[str] = []
        for brand, models in brand_groups.items():
            sorted_models = sorted(models, key=len, reverse=True)
            model_part = "|".join(
                re.escape(m) for m in sorted_models
            )  # Example: Vega from ai03 Vega
            if brand:
                parts.append(rf"(?:{re.escape(brand)}\s)?(?:{model_part})")
            else:
                parts.append(model_part)

        return re.compile("|".join(f"(?:{p})" for p in parts), re.IGNORECASE)

    _pattern = _build_pattern()

    @classmethod
    def _detect_products(cls, text: str) -> set[str]:
        """Returns all raw keyboard matches found in text"""
        return {match.group(0) for match in cls._pattern.finditer(text)}

    @staticmethod
    def _get_model_key(match: str) -> str:
        """Connects/Resolves a match (with or without brand prefix) to its model"""
        match_lower = match.lower()
        for model, brand in KEYBOARD_MODEL_TO_BRAND.items():
            if match_lower == model.lower():  # case where
                return model
            if brand and match_lower == f"{brand} {model}".lower():
                return model

        return match

    def _deduplicate(self, matches: set[str]) -> set[str]:
        """Keep the match with 'brand prefix' per unique product"""
        by_model: dict[str, str] = {}
        for match in matches:
            model = self._get_model_key(match)
            if model not in by_model or len(match) > len(by_model[model]):
                by_model[model] = match

        return set(by_model.values())
