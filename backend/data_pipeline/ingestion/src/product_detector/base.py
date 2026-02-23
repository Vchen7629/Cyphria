from src.products.mappings.computing import CPU_MODEL_TO_BRAND
from src.utils.validation import validate_string
from typing import Optional
from collections import defaultdict
from src.core.logger import StructuredLogger
from src.products.mappings.computing import CPU_REGEX_PATTERNS
from src.products.mappings.computing import GPU_MODEL_TO_BRAND
from src.products.mappings.computing import KEYBOARD_MODEL_TO_BRAND
from src.products.mappings.computing import MONITOR_MODEL_TO_BRAND
from src.products.detectors.gpu_pattern_builder import build_gpu_pattern
from src.products.detectors.gpu_pattern_builder import validate_gpu_match
import re

class ProductDetector:
    def __init__(
        self,
        pattern: re.Pattern[str],
        mapping: dict[str, str]
    ) -> None:
        self._pattern = pattern
        self._mapping = mapping

    def extract_products(self, text: str) -> list[str]:
        """
        Extract all product mentions from the text

        Args:
            text: comment text that we are checking

        Returns:
            list: list of all matching products strings or empty list if no products
        """
        if not text or not isinstance(text, str):
            return []

        detected_products = {match.group(0).strip() for match in self._pattern.finditer(text)}

        # Apply validation based on mapping type
        if self._mapping is GPU_MODEL_TO_BRAND:
            detected_products = {m for m in detected_products if validate_gpu_match(m, self._mapping)}

        # CPU uses substring containment deduplication
        if self._mapping is CPU_MODEL_TO_BRAND:
            deduplicated_products = self._deduplicate_regex(
                detected_products, 
                ['i3-', 'i5-', 'i7-', 'i9-', 'ryzen ', 'core ', 'pentium ', 'celeron ', 'threadripper ']
            )
        else:
            deduplicated_products = self._deduplicate_mapping(detected_products)

        # Sort with default case-sensitive sorting to match test expectations
        return sorted(list(deduplicated_products))

    def contains_product(self, text: str) -> bool:
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

        return bool(self._pattern.search(text))

    def _get_model_key(self, match: str) -> str:
        """Connects/Resolves a match (with or without brand prefix) to its model"""
        match_lower = match.lower()
        for model, brand in self._mapping.items():
            if match_lower == model.lower():
                return model
            if brand and match_lower == f"{brand} {model}".lower():
                return model

        return match

    def _deduplicate_mapping(self, matches: set[str]) -> set[str]:
        """Keep the match with 'brand prefix' per unique product"""
        by_model: dict[str, str] = {}
        for match in matches:
            model = self._get_model_key(match)
            if model not in by_model or len(match) > len(by_model[model]):
                by_model[model] = match

        return set(by_model.values())
    
    @staticmethod
    def _deduplicate_regex(matches: set[str], prefixes: list[str]) -> set[str]:
        """
        Remove matches taht are substrings of others with additional text at the start
        Keeps both if the longer match only adds a suffix at the end (different variants)
        
        Ex: 3900x3d and Ryzen 7 3900x3d, remove 3900x3d, i9-14900 and i9-14900k keep both
        """
        result = set()
        for match in matches:
            is_substring_with_prefix = any(
                match in other and not other.startswith(match)
                for other in matches if other != match
            )

            if not is_substring_with_prefix:
                result.add(match)
                
        return result

class BuildDetectorRegex:
    """Build regex for product topics needed to parse text to detect products"""

    # Mapping of topics to (data_mapping, optional_custom_builder)
    _TOPIC_CONFIGS = {
        "GPU": (GPU_MODEL_TO_BRAND, build_gpu_pattern),
        "CPU": (CPU_MODEL_TO_BRAND, None),
        "MONITOR": (MONITOR_MODEL_TO_BRAND, None),
        "MECHANICAL KEYBOARD": (KEYBOARD_MODEL_TO_BRAND, None),
    }

    @classmethod
    def process_all_topics(
        cls,
        topic_list: list[str],
        logger: Optional[StructuredLogger] = None
    ) -> list[Optional[re.Pattern[str]]]:
        """
        Build regex patterns for each topic in topic_list

        Args:
            topic_list: product topics to process like ['GPU', 'MONITOR']

        Returns:
            List of compiled regex patterns in the same order as topic_list;
            None for any topic that has no registered mapping
        """

        patterns: list[Optional[re.Pattern[str]]] = []

        for topic in topic_list:
            if not validate_string(topic, "topic", logger, log_error=True, raise_on_error=False):
                patterns.append(None)
                continue

            topic_upper = topic.upper().strip()
            config = cls._TOPIC_CONFIGS.get(topic_upper)

            if not config:
                if logger:
                    logger.warning(
                        event_type="Ingestion Run",
                        message=f"No mapping registered for topic '{topic}', skipping..."
                    )
                patterns.append(None)
                continue

            mapping, custom_builder = config

            if custom_builder:
                pattern = custom_builder(mapping)
            elif mapping is CPU_MODEL_TO_BRAND: 
                pattern = re.compile("|".join(CPU_REGEX_PATTERNS), re.IGNORECASE)
            else:
                pattern = cls._build_pattern(mapping)

            patterns.append(pattern)

        return patterns
    
    @staticmethod
    def _build_pattern(mapping: dict[str, str]) -> re.Pattern[str]:
        """Builds compiled regex from mapping, grouping models by brand prefix"""
        brand_groups: defaultdict[str, list[str]] = defaultdict(list)
        for model, brand in mapping.items():
            brand_groups[brand].append(model)

        parts: list[str] = []
        for brand, models in brand_groups.items():
            sorted_models = sorted(models, key=len, reverse=True)
            model_part = "|".join(re.escape(m) for m in sorted_models)  # Example: Vega from ai03 Vega
            if brand:
                parts.append(rf"\b(?:{re.escape(brand)}\s?)?(?:{model_part})\b")
            else:
                parts.append(rf"\b(?:{model_part})\b")

        return re.compile("|".join(f"(?:{p})" for p in parts), re.IGNORECASE)
