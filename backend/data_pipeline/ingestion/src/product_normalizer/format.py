def format_brand_model(brand: str, model: str) -> str:
    """Format product name with proper spacing (no space if brand ends with hyphen)"""
    separator = "" if brand.endswith("-") else " "
    return f"{brand}{separator}{model}"
