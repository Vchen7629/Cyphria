import re
from collections import defaultdict


def build_gpu_pattern(mapping: dict[str, str]) -> re.Pattern[str]:
    """Build GPU-specific regex pattern with suffix support"""
    brand_groups: defaultdict[str, set[str]] = defaultdict(set)

    # Extract base model numbers and group by brand
    for model, brand in mapping.items():
        match = re.match(r"^(\d{3,4})", model)
        if match:
            brand_groups[brand].add(match.group(1))

    parts: list[str] = []
    suffixes = r"(?:\s?(?:Ti|Super|FE|XT|XTX|GRE))?"

    for brand, numbers in brand_groups.items():
        number_part = "|".join(sorted(numbers, key=len, reverse=True))
        if brand:
            # (?<!\$) prevents matching prices like "$4090"
            parts.append(rf"(?<!\$)\b(?:{re.escape(brand)}\s?)?(?:{number_part}){suffixes}\b")
        else:
            parts.append(rf"(?<!\$)\b(?:{number_part}){suffixes}\b")

    return re.compile("|".join(f"(?:{p})" for p in parts), re.IGNORECASE)


def validate_gpu_match(match: str, mapping: dict[str, str]) -> bool:
    """Validate if a match is a real GPU (filters out false positives like CPU numbers)"""
    # Has brand prefix? Valid.
    if any(b.lower() in match.lower() for b in ["rtx", "gtx", "gt", "rx", "arc"]):
        return True

    # Bare number - check if it's a known model in the mapping
    num = re.match(r"(\d{3,4})", match)
    if not num:
        return False

    base_num = num.group(1)
    # Check if this base number exists in any model in the mapping
    return any(model.startswith(base_num) for model in mapping.keys())
