import re

class CPUDetector:
    """Detects CPU product mentions in comments"""
    CPU_REGEX_PATTERNS = [
        r"(?i)\b(?:Ryzen\s?\d?\s?(?:\s+Pro)?\s?\d{3,4}(?:x3d|xtx|x|xt|hx|hs|ge|gt|g|f)?|\d{3,4}(?:x3d|xtx|x|xt|hx|hs|ge|gt|g|f))\b", # regular ryzen cpus
        r"(?i)\b(?:(?:Ryzen\s+AI\s+(?:\d+\s+)?)?(?:Max\+?|HX)|Ryzen\s+AI(?:\s+\d+)?)\s+\d{3,4}\b", # ryzen AI cpus
        r"(?i)\b(?:(?:Ryzen\s+)?Threadripper(?:\s+Pro)?\s+\d{4}(?:W?X)?|Ryzen\s+\d{4}(?:W?X)?|\d{4}W?X)\b", # ryzen threadripper cpus
        r"(?i)\b(?:i[3579]-\d{3,5}(?:K[FS]?|U|H|T|E|TE|S|P|X)?|Core(?:\s+Ultra)?\s+\d+\s+\d{3,5}(?:K[FS]?|U|H|T|E|TE|S|P|X)?|\d{3,5}(?:K[FS]?|U|H|T|E|TE|S|P|X))\b", # regular intel cpus
        r"(Pentium|Celeron)?\s?(Gold|Silver)?\s?([G|N|J|U|Y]\d{3,5}(?:TE|T|F|U|Y|E)?)" # intel pentium and celeron cpus
    ]

    def __init__(self) -> None:
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.CPU_REGEX_PATTERNS
        ]

    def extract_cpus(self, text: str) -> list[str]:
        """
        Extract all CPU mentions from the text

        Args:
            text: comment text that we are checking

        Returns:
            list: list of all matching cpu name strings or empty list if no cpus
        """
        if not text:
            return []

        detected = set()

        for pattern in self.compiled_patterns:
            for match in pattern.finditer(text):
                detected.add(match.group(0).strip())

        # returns a sorted list, checks if any of the detected cpu names isnt contained
        # within another name to prevent double matching
        # For example: Threadripper 9980X matches both 9980X and Threadripper 9980X,
        # this will just keep Threadripper 9980X
        return sorted(
            match for match in detected
            if not any(match in other for other in detected if other != match)
        )

    def contains_cpu(self, text: str) -> bool:
        """
        Check if comment text contains any CPU mention

        Args:
            text: comment text string we're checking for

        Returns:
            bool: true if there is at least one mention of CPU
                    false otherwise
        """
        return len(self.extract_cpus(text)) > 0
