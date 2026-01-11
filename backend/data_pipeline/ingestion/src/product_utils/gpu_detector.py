import re

class GPUDetector:
    """Detects GPU product mentions in comments"""
    # Known GPU model numbers for validation
    KNOWN_NVIDIA_MODELS = {
        '5090', '5080', '5070', '5060', '5050',
        '4090', '4080', '4070', '4060',
        '3090', '3080', '3070', '3060', '3050',
        '2080', '2070', '2060',
        '1080', '1070', '1060', '1050', '1030',
        '980', '970', '960', '950'
    }

    KNOWN_AMD_MODELS = {
        '9070', '9060',
        '7900', '7800', '7700', '7600',
        '6950', '6900', '6800', '6750', '6700', '6650', '6600', '6500', '6400',
        '5700', '5600', '5500', '5300'
    }

    KNOWN_INTEL_MODELS = {
        'A770', 'A750', 'A580', 'A380', 'A310',
        'B770', 'B580', 'B570',
    }

    GPU_PATTERNS = [
        # Full names with brand: RTX 4090, GTX 1080 Ti, etc
        r'\b(RTX|GTX|GT)\s?(\d{4})(\s?(Ti|SUPER|Super|FE))?\b',
        r'\bRX\s?(\d{3,4})(\s?(XT|XTX))?\b',
        r'\bArc\s?(A|B)(\d{3})\b',
        # Bare model numbers: 4090, 3080, 1080 Ti, etc
        r'(?<!rtx\s)(?<!rtx)(?<!gtx\s)(?<!gtx)(?<!gt\s)(?<!gt)(?<!rx\s)(?<!rx)(?<!arc\s)(?<!arc)(?<!\$)\b(\d{3,4})(\s?(Ti|SUPER|Super|FE|XT|XTX))?\b',
    ]

    def __init__(self) -> None:
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.GPU_PATTERNS
        ]

    def extract_gpus(self, text: str) -> list[str]:
        """
        Extract all GPU mentions from the text

        Args:
            text: comment text that we are checking

        Returns:
            list: list of all matching gpu name strings
        """
        detected = set()

        for pattern in self.compiled_patterns:
            for match in pattern.finditer(text):
                gpu_name = match.group(0).lower().strip()

                # if it's a bare number (no brand prefix), validate it
                if not any(brand in gpu_name for brand in ['rtx', 'gtx', 'gt', 'rx', 'arc']):
                    # Extract just the numeric part (e.g., "3080" from "3080fe" or "3080 ti")
                    num_match = re.match(r'(\d{3,4})', gpu_name)
                    if num_match is None:
                        continue
                    base_num = num_match.group(1)
                    # skip numbers not matching the known gpu numbers
                    if base_num not in self.KNOWN_NVIDIA_MODELS and base_num not in self.KNOWN_AMD_MODELS and base_num not in self.KNOWN_INTEL_MODELS:
                        continue
                
                detected.add(gpu_name)

        return sorted(list(detected))

    def contains_gpu(self, text: str) -> bool:
        """
        Check if comment text contains any GPU mention

        Args:
            text: comment text string we're checking for

        Returns:
            bool: true if there is at least one mention of gpu
                    false otherwise
        """
        return len(self.extract_gpus(text)) > 0