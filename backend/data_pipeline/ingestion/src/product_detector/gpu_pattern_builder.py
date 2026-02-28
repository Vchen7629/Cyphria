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


def validate_gpu_match(matches: set[str], mapping: dict[str, str]) -> set[str]:
    """
    Validate if a match is a real GPU (filters out false positives like CPU numbers)
    and returns all matching
    """
    def _is_valid(match: str) -> bool:
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
    
    valid = {m for m in matches if _is_valid(m)}

    return _deduplicate_names(valid)    

def _deduplicate_names(valid_names: set[str]) -> set[str]:
    """For the same base number, keep the longest match (brand-prefixed wins)"""
    by_number: dict[str, str] = {}
    for match in valid_names:
        num = re.search(r"(\d{3,4})", match)
        key = num.group(1) if num else match
        if key not in by_number or len(match) > len(by_number[key]):
            by_number[key] = match

    return set(by_number.values())
