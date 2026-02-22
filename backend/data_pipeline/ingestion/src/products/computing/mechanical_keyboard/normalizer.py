from typing import Optional
from src.products.computing.mechanical_keyboard.mappings import KEYBOARD_MODEL_TO_BRAND

class MechanicalKeyboardNormalizer:
    _UPPER_MODEL_TO_BRAND = {model.upper(): brand for model, brand in KEYBOARD_MODEL_TO_BRAND.items()}

    def normalize_keyboard_list(self, keyboard_list: list[str]) -> list[str]:
        """
        Normalize mechanical keyboard names to 'Brand Model' format

        Args:
            keyboard_list: list of unnormalized mechanical keyboard names

        Returns:
            a list containing the normalized mechanical keyboard names
        """
        if not keyboard_list or not isinstance(keyboard_list, list):
            return []

        normalized_names = set()

        for keyboard in keyboard_list:
            normalized_name = self._normalize_name(keyboard)
            if not normalized_name:
                continue
            normalized_names.add(normalized_name)

        return list(normalized_names)

    @classmethod
    def _normalize_name(cls, keyboard: str) -> Optional[str]:
        """
        Normalize one mechanical keyboard name

        Args:
            keyboard: the raw unnormalized mechanical keyboard name

        Returns:
            the normalized keyboard name in format 'Brand Model'
        """
        if not isinstance(keyboard, str):
            return None

        raw_keyboard_name = keyboard.strip()
        brand = cls._UPPER_MODEL_TO_BRAND.get(raw_keyboard_name.upper())

        if brand is None:
            return None

        return f"{brand} {raw_keyboard_name}" if brand else raw_keyboard_name
