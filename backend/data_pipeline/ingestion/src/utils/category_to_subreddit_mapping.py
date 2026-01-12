from src.core.logger import StructuredLogger

def category_to_subreddit_mapping(logger: StructuredLogger | None, category: str) -> list[str]:
    """
    This maps a product category to a list of subreddits

    Args:
        logger: the structured logger instance for logging errors
        category: the product category like "GPU", "Laptop", etc

    Returns:
        a list of subreddits corresponding the product category
    """
    CATEGORY_SUBREDDITS = {
        "GPU": ["nvidia", "radeon", "amd", "IntelArc", "buildapc", "gamingpc", "pcbuild", "hardware"]
    }

    input_category = category.upper().strip()

    if input_category not in CATEGORY_SUBREDDITS:
        if logger:
            logger.error(
                event_type="data ingestion category",
                message=f"Unknown category: {input_category}"
            )
        return []

    return CATEGORY_SUBREDDITS[input_category]