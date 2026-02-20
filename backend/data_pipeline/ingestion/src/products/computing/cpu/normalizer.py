from typing import Dict
from typing import Tuple
from typing import Optional
from src.core.logger import StructuredLogger
from src.products.computing.cpu.mappings import INTEL_MODEL_TO_TIER
from src.products.computing.cpu.mappings import AMD_MODEL_TO_TIER
import re


class CPUNameNormalizer:
    def __init__(self, logger: Optional[StructuredLogger]) -> None:
        self.logger = logger

    def normalize_cpu_list(self, cpu_list: list[str]) -> list[str]:
        """
        Public method that use calls to normalize cpu names to 'Vendor Brand TierModel' format

        Args:
            cpu_list: list of unnormalized cpu names

        Returns:
            a list containing the normalized cpu names
        """
        if not cpu_list:
            return []

        normalized_names = set()

        for cpu in cpu_list:
            normalized_name = self._normalize_name(cpu)
            if not normalized_name:
                continue
            normalized_names.add(normalized_name)

        return list(normalized_names)

    def _lookup_and_format(
        self, model: str, mapping: Dict[str, Tuple[str, str]], vendor: str
    ) -> Optional[str]:
        """
        Look up model in mapping and format as 'Vendor Brand TierModel'

        Args:
            model: the raw_cpu_name string
            mapping: the dict mapping the cpu_name to a tuple of brand, tier strings
            vendor: either AMD or Intel

        Returns:
            the normalized cpu name or None if its not found in the mapping
        '"""
        info = mapping.get(model)
        if info:
            brand, tier = info
            return f"{vendor} {brand} {tier}{model}"
        return None

    def _normalize_name(self, cpu: str) -> Optional[str]:
        """
        Normalize one cpu name

        Args:
            cpu: the raw unnormalized cpu name

        Returns:
            the normalized cpu name in format 'Vendor Brand TierModel'
        """
        raw_cpu_name = cpu.strip()
        cpu_name_caps = raw_cpu_name.upper()
        logger = self.logger

        # Try bare number matching first for both vendors
        if cpu_name_caps in AMD_MODEL_TO_TIER:
            return self._lookup_and_format(cpu_name_caps, AMD_MODEL_TO_TIER, "AMD")
        if cpu_name_caps in INTEL_MODEL_TO_TIER:
            return self._lookup_and_format(cpu_name_caps, INTEL_MODEL_TO_TIER, "Intel")

        # Try vendor-specific normalization
        amd_result = self._normalize_amd(raw_cpu_name, cpu_name_caps)
        if amd_result:
            return amd_result

        intel_result = self._normalize_intel(raw_cpu_name, cpu_name_caps)
        if not intel_result:
            if logger:
                logger.debug(
                    event_type="ingestion_service run",
                    message="cpu unable to be normalized with intel and amd",
                )
            return None

        return intel_result

    def _normalize_amd(self, raw_cpu_name: str, cpu_name_caps: str) -> Optional[str]:
        """
        Normalize AMD CPU names (Ryzen, Threadripper)

        Args:
            raw_cpu_name: the unformatted cpu name string with whitespace removed
            cpu_name_caps: the unformatted cpu name string in all caps

        Returns:
            the amd specific formatted cpu name if it matches one of the regexes, None otherwise
        """
        # Ryzen without tier (Ryzen 5900X)
        if re.match(r"(?i)^ryzen\s+\d{3,4}\w*$", cpu_name_caps):
            model = cpu_name_caps.split(None, 1)[1]
            return self._lookup_and_format(model, AMD_MODEL_TO_TIER, "AMD")

        # Threadripper without Ryzen prefix (Threadripper Pro 3995WX, Threadripper 3970X)
        match = re.match(r"(?i)^threadripper\s+(?:pro\s+)?(\d{3,4}(?:W?X)\w*)$", cpu_name_caps)
        if match:
            model = match.group(1)
            return self._lookup_and_format(model, AMD_MODEL_TO_TIER, "AMD")

        # Already formatted (Ryzen 9 5900X, Threadripper Pro 3995WX)
        if re.match(r"(?i)^(ryzen|threadripper)", raw_cpu_name):
            return f"AMD {raw_cpu_name}"

        return None

    def _normalize_intel(self, raw_cpu_name: str, cpu_name_caps: str) -> Optional[str]:
        """
        Normalize Intel CPU names (Core, Pentium, Celeron)

        Args:
            raw_cpu_name: the unformatted cpu name string with whitespace removed
            cpu_name_caps: the unformatted cpu name string in all caps

        Returns:
            the intel specific formatted cpu name if it matches one of the regexes, None otherwise
        """
        # Core prefix with bare model number (Core 10900K, Core 7740X)
        if re.match(r"(?i)^Core\s+\d{3,4}\w*$", cpu_name_caps):
            model = cpu_name_caps.split(None, 1)[1]
            return self._lookup_and_format(model, INTEL_MODEL_TO_TIER, "Intel")

        # i-series prefix — extract model after last hyphen
        # handles: i7-10900K, Core i7-10900K, i7-7740X, Core i7-7740X
        if re.match(r"(?i)^(?:core\s+)?i[3579]", raw_cpu_name) and "-" in raw_cpu_name:
            model = raw_cpu_name.rsplit("-", 1)[-1].upper()
            return self._lookup_and_format(model, INTEL_MODEL_TO_TIER, "Intel")

        # Core Ultra without tier number (Core Ultra 285K, Ultra 285K)
        match = re.match(r"(?i)^(?:core\s+)?ultra\s+(\d{3,5}\w*)$", raw_cpu_name)
        if match:
            model = match.group(1).upper()
            return self._lookup_and_format(model, INTEL_MODEL_TO_TIER, "Intel")

        # Pentium/Celeron without grade (Pentium G6500, Celeron G5900)
        match = re.match(r"(?i)^(pentium|celeron)\s+([a-z]\d{3,5}\w*)$", raw_cpu_name)
        if match:
            model = match.group(2).upper()
            return self._lookup_and_format(model, INTEL_MODEL_TO_TIER, "Intel")

        # Already formatted (Core i7-10900K, Pentium Gold G6500, Core Ultra 9 285K)
        if re.match(r"(?i)^(core\s(?:Ultra\s\d|i[3579]-)|pentium|celeron)", raw_cpu_name):
            return f"Intel {raw_cpu_name}"

        return None
