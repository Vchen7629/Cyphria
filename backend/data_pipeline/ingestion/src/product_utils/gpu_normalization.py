import re


class GPUNameNormalizer:
    """Normalizes Variations of GPU names into one format"""

    # Pattern to parse GPU strings: captures brand, model, and variant
    # Examples: "rtx 4090", "4090 ti", "rx 7900 xtx", "arc a770"
    GPU_PARSE_PATTERN = re.compile(
        r"(?:(rtx|gtx|gt|rx|arc)\s?)?"  # Optional brand prefix
        r"([a-z]?\d{3,4})"  # Model number (may have letter prefix for Intel)
        r"(?:\s?(ti|super|fe|xtx|xt))?",  # Optional variant
        re.IGNORECASE,
    )

    # Map model numbers to their brand (for bare numbers like "4090")
    MODEL_TO_BRAND = {
        "5090": "NVIDIA",
        "5080": "NVIDIA",
        "5070": "NVIDIA",
        "5060": "NVIDIA",
        "5050": "NVIDIA",
        "4090": "NVIDIA",
        "4080": "NVIDIA",
        "4070": "NVIDIA",
        "4060": "NVIDIA",
        "3090": "NVIDIA",
        "3080": "NVIDIA",
        "3070": "NVIDIA",
        "3060": "NVIDIA",
        "3050": "NVIDIA",
        "2080": "NVIDIA",
        "2070": "NVIDIA",
        "2060": "NVIDIA",
        "1080": "NVIDIA",
        "1070": "NVIDIA",
        "1060": "NVIDIA",
        "1050": "NVIDIA",
        "1030": "NVIDIA",
        "980": "NVIDIA",
        "970": "NVIDIA",
        "960": "NVIDIA",
        "950": "NVIDIA",
        "9070": "AMD",
        "9060": "AMD",
        "7900": "AMD",
        "7800": "AMD",
        "7700": "AMD",
        "7600": "AMD",
        "6950": "AMD",
        "6900": "AMD",
        "6800": "AMD",
        "6750": "AMD",
        "6700": "AMD",
        "6650": "AMD",
        "6600": "AMD",
        "6500": "AMD",
        "6400": "AMD",
        "5700": "AMD",
        "5600": "AMD",
        "5500": "AMD",
        "5300": "AMD",
        "A770": "Intel",
        "A750": "Intel",
        "A580": "Intel",
        "A380": "Intel",
        "A310": "Intel",
        "B770": "Intel",
        "B580": "Intel",
        "B570": "Intel",
    }

    def _determine_brand(self, brand_prefix: str | None, model: str) -> str | None:
        """
        Determine manufacturer from prefix or model number

        Args:
            brand_prefix: optional string like rtx, gtx, gt, rx, or arc
            model: string for the model number like 4090 in RTX 4090

        Returns:
            brand name, either NVIDIA, AMD, or Intel, None otherwise
        """
        if brand_prefix:
            prefix_lower = brand_prefix.lower()
            if prefix_lower in ["rtx", "gtx", "gt"]:
                return "NVIDIA"
            elif prefix_lower == "rx":
                return "AMD"
            elif prefix_lower == "arc":
                return "Intel"

        # for bare numbers, look up in mapping
        return self.MODEL_TO_BRAND.get(model.upper(), None)

    def _format_name(
        self, brand: str, model: str, brand_prefix: str | None, variant: str | None
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

    def _normalize(self, detected_gpu: str) -> str | None:
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

        brand = self._determine_brand(brand_prefix, model)
        if not brand:
            return None

        return self._format_name(brand, model, brand_prefix, variant)

    def normalize_gpu_list(self, detected_products: list[str]) -> list[str]:
        """
        Normalize a list of detected GPU names to canonical format

        Args:
            detected_products: list of raw GPU names from GPUDetector

        Returns:
            list of unique formatted product names with duplicates removed
        """
        formatted_products = set()

        for gpu in detected_products:
            normalized: str | None = self._normalize(gpu)
            if normalized:
                formatted_products.add(normalized)

        return sorted(list(formatted_products))
