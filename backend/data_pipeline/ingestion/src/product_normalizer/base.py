from typing import Callable
from typing import Optional
from shared_core.logger import StructuredLogger
from src.utils.validation import validate_string
from src.product_normalizer.cpu import CPUNormalizer
from src.product_normalizer.gpu import GPUNormalizer
from src.product_mappings.computing import GPU_MODEL_TO_BRAND
from src.product_mappings.computing import CPU_MODEL_TO_BRAND
from src.product_mappings.computing import MONITOR_MODEL_TO_BRAND
from src.product_mappings.computing import KEYBOARD_MODEL_TO_BRAND
from src.product_mappings.computing import LAPTOP_MODEL_TO_BRAND


class ProductNormalizer:
    # Type alias for config tuple (mapping_dict, optional_normalizer_function)
    TopicConfig = tuple[dict[str, str], Optional[Callable[[str, dict[str, str]], Optional[str]]]]

    _TOPIC_CONFIGS: dict[str, TopicConfig] = {
        "GPU": (
            {model.upper(): brand for model, brand in GPU_MODEL_TO_BRAND.items()},
            GPUNormalizer().normalize_name,
        ),
        "CPU": (
            {model.upper(): brand for model, brand in CPU_MODEL_TO_BRAND.items()},
            CPUNormalizer().normalize_name,
        ),
        "MONITOR": (MONITOR_MODEL_TO_BRAND, None),
        "MECHANICAL KEYBOARD": (KEYBOARD_MODEL_TO_BRAND, None),
        "LAPTOP": (LAPTOP_MODEL_TO_BRAND, None),
    }

    def __init__(self, logger: Optional[StructuredLogger] = None) -> None:
        self._logger = logger

    def normalize_product_list(self, topic: str, product_list: list[str]) -> list[str]:
        """
        Normalize product names to 'Brand Model' format

        Args:
            product_list: list of unnormalized mechanical keyboard names

        Returns:
            a list containing the normalized mechanical keyboard names
        """
        if not product_list or not isinstance(product_list, list):
            return []

        if not validate_string(
            topic, "product_topic", self._logger, log_error=True, raise_on_error=False
        ):
            return []

        normalized_names = set()

        for product_name in product_list:
            normalized_name = self._normalize_name(product_name, topic)
            if not normalized_name:
                continue
            normalized_names.add(normalized_name)

        return sorted(normalized_names)

    @classmethod
    def _normalize_name(
        cls, product_name: str, topic: str, logger: Optional[StructuredLogger] = None
    ) -> Optional[str]:
        """
        Normalize one product_name name

        Args:
            product_name: the raw unnormalized product_name

        Returns:
            the normalized product_name name in format 'Brand Model'
        """
        if not isinstance(product_name, str) or not isinstance(topic, str):
            return None

        raw_product_name = product_name.strip()

        config = cls._TOPIC_CONFIGS.get(topic.strip().upper(), None)
        if not config:
            if logger:
                logger.warning(
                    event_type="Ingestion Run",
                    message=f"No mapping registered for topic '{topic}', skipping...",
                )
            return None

        data_mapping, custom_normalizer = config

        # If there's a custom normalizer, use it (it will check mapping internally)
        if custom_normalizer:
            return custom_normalizer(raw_product_name, data_mapping)

        # Otherwise use default mapping logic
        # Try direct lookup first, only model name, then try stripping leading brand prefix
        for model_key, model_brand in data_mapping.items():
            if raw_product_name.upper() in (
                model_key.upper(),
                f"{model_brand} {model_key}".upper(),
            ):
                return f"{model_brand} {model_key}" if model_brand else model_key

        return None
