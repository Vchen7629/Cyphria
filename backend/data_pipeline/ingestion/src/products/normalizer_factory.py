from typing import Optional
from src.core.logger import StructuredLogger
from src.utils.validation import validate_string
from src.products.computing.gpu.normalizer import GPUNameNormalizer
from src.products.computing.cpu.normalizer import CPUNameNormalizer
from src.products.computing.mechanical_keyboard.normalizer import MechanicalKeyboardNormalizer


class NormalizerFactory:
    """Factory that returns normalized product names based on category"""

    @staticmethod
    def normalize(
        product_topic: str, product_list: list[str], logger: Optional[StructuredLogger] = None
    ) -> Optional[list[str]]:
        """
        Normalize the product list for the given product topic

        Args:
            product_topic: Product topic (e.g., 'gpu', 'laptop', 'headphone')
            product_list: List of product names to normalize

        Returns:
            List of normalized product names or none if no product topic/list input param

        Raises:
            ValueError: If product_topic is not supported
        """
        if not validate_string(
            product_topic, "product_topic", logger, log_error=True, raise_on_error=False
        ):
            return None

        match product_topic.lower().strip():
            case "gpu":
                return GPUNameNormalizer().normalize_gpu_list(product_list)
            case "cpu":
                return CPUNameNormalizer(logger).normalize_cpu_list(product_list)
            case "MECHANICAL KEYBOARD":
                return MechanicalKeyboardNormalizer().normalize_keyboard_list(product_list)
            case _:
                raise ValueError(f"Unsupported product_topic: '{product_topic}'. Supported: gpu")
