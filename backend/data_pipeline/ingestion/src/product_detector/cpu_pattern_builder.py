import re
from src.product_mappings.computing import CPU_REGEX_PATTERNS


CPU_DEDUP_PREFIXES = [
    "i3-",
    "i5-",
    "i7-",
    "i9-",
    "ryzen ",
    "core ",
    "pentium ",
    "celeron ",
    "threadripper ",
]


def build_cpu_pattern(_mapping: dict[str, str]) -> re.Pattern[str]:
    """Build CPU-specific regex pattern from CPU_REGEX_PATTERNS"""
    return re.compile("|".join(CPU_REGEX_PATTERNS), re.IGNORECASE)


def validate_cpu_match(matches: set[str], _mapping: dict[str, str]) -> set[str]:
    """
    Remove matches that are substrings of others with additional text at the start.
    Keeps both if the longer match only adds a suffix at the end (different variants).

    Ex: 3900x3d and Ryzen 7 3900x3d -> remove 3900x3d
        i9-14900 and i9-14900k -> keep both
    """
    result = set()
    for match in matches:
        is_substring_with_prefix = any(
            match in other and not other.startswith(match)
            for other in matches
            if other != match
        )

        if not is_substring_with_prefix:
            result.add(match)

    return result
