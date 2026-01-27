from typing import Optional
from src.core.logger import StructuredLogger
from src.product_utils.gpu_normalization import GPUNameNormalizer


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
        if not product_topic or not product_list or product_topic.strip() == "":
            if logger:
                logger.error(
                    event_type="ingestion_service run",
                    message="Missing product topic, can't normalize",
                )
            return None
        match product_topic.lower().strip():
            case "gpu":
                return GPUNameNormalizer().normalize_gpu_list(product_list)
            case _:
                raise ValueError(f"Unsupported product_topic: '{product_topic}'. Supported: gpu")
