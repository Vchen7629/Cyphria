from typing import Optional
import re


class CPUNormalizer:
    # pattern list containing regexes
    BASE_MODEL_PATTERNS: list[tuple[str, str, int]] = [
        ("Core i-series X variant", r"^(?:core\s+)?i[3579]\s+X\s+i[3579]-(\w+)$", 1),
        ("Core i-series with hyphen", r"^(?:core\s+)?i[3579]-(\w+)$", 1),
        ("Core with model", r"^core\s+(\d{3,5}\w*)$", 1),
        ("Core Ultra", r"^core\s+ultra\s+(?:\d\s+)?(\d{3,5}\w*)$", 1),
        ("Pentium", r"^pentium(?:\s+\w+)?\s+([a-z]\d{3,5}\w*)$", 1),
        ("Celeron", r"^celeron(?:\s+\w+)?\s+([a-z]\d{3,5}\w*)$", 1),
    ]

    def normalize_name(self, cpu: str, product_mapping: dict[str, str]) -> Optional[str]:
        """
        Normalize CPU name using mapping-first approach

        Logic Flow:
        1. Direct mapping lookup (exact match)
        2. Extract base model and lookup in mapping
        3. Vendor-specific regex normalization (fallback)

        Args:
            cpu: raw unnormalized cpu name
            product_mapping: the dictionary containing base model to brand mapping
        """
        raw_cpu_name = cpu.strip()
        cpu_name_upper = raw_cpu_name.upper()

        if (result := self._try_direct_lookup(cpu_name_upper, raw_cpu_name, product_mapping)) is not None:
            return result

        if (result := self._try_base_model_lookup(raw_cpu_name, product_mapping)) is not None:
            return result

        if (result := self._normalize_amd(raw_cpu_name, cpu_name_upper, product_mapping)) is not None:
            return result

        if (result := self._normalize_intel(raw_cpu_name, cpu_name_upper)) is not None:
            return result

        return None
    
    @classmethod
    def _extract_base_model(cls, cpu_name: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract base model from CPU name using pattern registry
        Returns: (uppercase_for_lookup, original_case_for_display)
        """
        for _description, pattern, group_idx in cls.BASE_MODEL_PATTERNS:
            if match := re.match(pattern, cpu_name, re.IGNORECASE):
                original = match.group(group_idx)
                return (original.upper(), original)
        return (None, None)

    @staticmethod
    def _format_cpu_name(brand: str, model: str) -> str:
        """Format CPU name with proper spacing (no space if brand ends with hyphen)"""
        separator = "" if brand.endswith("-") else " "
        return f"{brand}{separator}{model}"

    @staticmethod
    def _normalize_amd(raw_name: str, name_upper: str, product_mapping: dict[str, str]) -> Optional[str]:
        model_match = None

        # Ryzen without tier (e.g., "Ryzen 5500X3D")
        if match := re.match(r"^ryzen\s+(\d{3,4}\w*)$", name_upper, re.IGNORECASE):
            model_match = match.group(1)

        # Threadripper with optional Ryzen prefix (e.g., "Threadripper Pro 7995WX" or "Ryzen Threadripper Pro 7995WX")
        elif match := re.match(r"(?i)^(?:ryzen\s+)?threadripper\s+(?:pro\s+)?(\d{3,4}(?:W?X)\w*)$", name_upper):
            model_match = match.group(1)

        if model_match and model_match in product_mapping:
            brand = product_mapping[model_match]
            return f"{brand} {model_match}" if brand else None

        # Already formatted with tier (e.g., "Ryzen 5 5900X", "Ryzen Threadripper Pro 7995WX")
        if re.match(r"(?i)^ryzen\s+(?:\d\s+\d{3,4}\w*|threadripper)", raw_name):
            return f"AMD {raw_name}"

        return None

    @staticmethod
    def _normalize_intel(raw_name: str, name_upper: str) -> Optional[str]:
        """Normalize Intel CPU names - fallback only (mapping should handle most)"""
        # Core prefix with bare model number
        if re.match(r"(?i)^Core\s+\d{3,4}\w*$", name_upper):
            model = name_upper.split(None, 1)[1]
            return f"Intel {model}"

        # i-series prefix — extract model after hyphen
        if re.match(r"(?i)^(?:core\s+)?i[3579]", raw_name) and "-" in raw_name:
            model = raw_name.rsplit("-", 1)[-1].upper()
            return f"Intel {model}"

        # Core Ultra without tier number
        if match := re.match(r"(?i)^(?:core\s+)?ultra\s+(\d{3,5}\w*)$", raw_name):
            return f"Intel {match.group(1).upper()}"

        # Pentium/Celeron without grade
        if match := re.match(r"(?i)^(pentium|celeron)\s+([a-z]\d{3,5}\w*)$", raw_name):
            return f"Intel {match.group(2).upper()}"

        # Already formatted
        if re.match(r"(?i)^(core\s(?:Ultra\s\d|i[3579]-)|pentium|celeron)", raw_name):
            return f"Intel {raw_name}"

        return None

    def _try_direct_lookup(
        self, cpu_upper: str, cpu_original: str, mapping: dict[str, str]
    ) -> Optional[str]:
        """Try looking up the CPU name directly in the mapping"""
        if cpu_upper in mapping:
            brand = mapping[cpu_upper]
            return self._format_cpu_name(brand, cpu_original) if brand else None
        return None

    def _try_base_model_lookup(
        self, raw_cpu_name: str, mapping: dict[str, str]
    ) -> Optional[str]:
        """Extract base model and lookup in mapping (e.g., 'Core 3930K' -> '3930K')"""
        base_upper, base_original = self._extract_base_model(raw_cpu_name)
        if base_upper and base_upper in mapping:
            brand = mapping[base_upper]
            if base_original:
                return self._format_cpu_name(brand, base_original) if brand else None
        return None