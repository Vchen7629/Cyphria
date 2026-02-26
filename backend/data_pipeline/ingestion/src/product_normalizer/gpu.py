from typing import Optional
import re


class GPUNormalizer:
    # Series to brand mapping
    SERIES_TO_BRAND: dict[str, str] = {
        "rtx": "NVIDIA",
        "gtx": "NVIDIA",
        "gt": "NVIDIA",
        "rx": "AMD",
        "arc": "Intel",
    }

    # Pattern to parse GPU strings: captures brand, model, and variant
    # Examples: "rtx 4090", "4090 ti", "rx 7900 xtx", "arc a770"
    GPU_PARSE_PATTERN = re.compile(
        r"(?:(rtx|gtx|gt|rx|arc)\s?)?"  # Optional brand prefix
        r"([a-z]?\d{3,4})"  # Model number (may have letter prefix for Intel)
        r"(?:\s?(ti|super|fe|xtx|xt))?",  # Optional variant
        re.IGNORECASE,
    )

    def normalize_name(self, detected_gpu: str, product_mapping: dict[str, str]) -> Optional[str]:
        """
        Normalize a detected GPU Name into one format

        Args:
            detected_gpu: Raw GPU name from GPUDetector

        Returns:
            GPU name normalized into one product name format or None if it cant parse
        """
        match = self.GPU_PARSE_PATTERN.match(detected_gpu.lower().strip())
        if not match:
            return None

        brand_prefix, model, variant = match.groups()

        brand = self._determine_brand(brand_prefix, model, product_mapping)
        if not brand:
            return None

        return self._format_name(brand, model, brand_prefix, variant)

    @classmethod
    def _determine_brand(
        cls, brand_prefix: Optional[str], model: str, product_mapping: dict[str, str]
    ) -> Optional[str]:
        """
        Determine manufacturer from prefix or model number

        Args:
            brand_prefix: optional string like rtx, gtx, gt, rx, or arc
            model: string for the model number like 4090 in RTX 4090

        Returns:
            brand name, either NVIDIA, AMD, or Intel, None otherwise
        """
        if brand_prefix and (brand := cls.SERIES_TO_BRAND.get(brand_prefix.lower())):
            return brand

        # for bare numbers, look up series in mapping and convert to brand
        if series := product_mapping.get(model.upper(), None):
            return cls.SERIES_TO_BRAND.get(series.lower())

        return None

    @staticmethod
    def _format_name(
        brand: str, model: str, brand_prefix: str | None, variant: str | None
    ) -> str | None:
        """
        Build formatted name based on brand

        Args:
            brand: brand string, either NVIDIA, AMD, or Intel
            model: the gpu number such as 4090 in RTX 4090
            brand_prefix: optional string such as rtx, gtx, gt, rx, or arc
            variant: optional string such as Ti, Super, XTX

        Returns:
            the formatted gpu name like NVIDIA RTX 4090 or AMD RX 7900 XTX
        """
        if brand == "NVIDIA":
            if brand_prefix:
                series = brand_prefix.upper()
            else:
                if int(model) >= 2000:
                    series = "RTX"
                elif int(model) == 1030:
                    series = "GT"
                else:
                    series = "GTX"

            # Format variant (Ti, Super, etc)
            variant_str = ""
            if variant and variant.lower() != "fe":
                variant_str = (
                    f" {variant.upper() if variant.lower() == 'super' else variant.capitalize()}"
                )

            return f"NVIDIA {series} {model}{variant_str}"
        elif brand == "AMD":
            variant_str = f" {variant.upper()}" if variant else ""
            return f"AMD RX {model}{variant_str}"
        elif brand == "Intel":
            return f"Intel Arc {model.upper()}"

        return None
