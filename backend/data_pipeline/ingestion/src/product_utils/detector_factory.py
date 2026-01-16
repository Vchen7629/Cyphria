from src.product_utils.gpu_detector import GPUDetector
from typing import Any

class ProductDetectorWrapper:
    """Wrapper that provides a universal interface for all product detectors"""
    def __init__(self, detector: Any, contains_method: str, extract_method: str) -> None:
        self._detector = detector
        self._contains_method = contains_method
        self._extract_method = extract_method
    
    def contains_product(self, text: str) -> bool:
        """
        Universal method to check if text contains any product mention

        Args:
            text: Comment text to check if it contains any product mention

        Returns:
            True if it contains a product mention, False otherwise
        """
        return getattr(self._detector, self._contains_method)(text)

    def extract_products(self, text: str) -> list[str]:
        """
        Universal method to extract all product mentions from the comment text

        Args:
            text: Comment text to check if it contains any products
        
        Returns:
            A list of product names
        """
        return getattr(self._detector, self._extract_method)(text)

class DetectorFactory:
    """Detector Factory that returns the appropriate detector based on the product category"""
    @staticmethod
    def get_detector(category: str) -> ProductDetectorWrapper:
        """
        Get the appropriate detector for the given product category
        this detector is used for checking if the comment contains a mention
        0f a product or how many products mentioned for the specified category

        Args:
            category: Product category, ie 'gpu', 'laptop', 'headphone'

        Returns:
            ProductDetectorWrapper with universal interface

        Raises:
            ValueError: If category is not supported
        """
        match category.lower().strip():
            case "gpu":
                return ProductDetectorWrapper(
                    GPUDetector(),
                    contains_method='contains_gpu',
                    extract_method='extract_gpus'
                )
            case _:
                raise ValueError(
                    f"Unsupported category: '{category}'. Supported: gpu"
                )