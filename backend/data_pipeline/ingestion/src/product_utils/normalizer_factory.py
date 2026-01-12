from src.product_utils.gpu_normalization import GPUNameNormalizer

class NormalizerFactory:
    """Factory that returns normalized product names based on category"""

    @staticmethod
    def normalize(category: str, product_list: list[str]) -> list[str]:
        """
        Normalize the product list for the given product category
        
        Args:
            category: Product category (e.g., 'gpu', 'laptop', 'headphone')
            product_list: List of product names to normalize
            
        Returns:
            List of normalized product names
            
        Raises:
            ValueError: If category is not supported
        """
        match category.lower().strip():
            case "gpu":
                return GPUNameNormalizer().normalize_gpu_list(product_list)
            case _:
                raise ValueError(
                    f"Unsupported category: '{category}'. Supported: gpu"
                )