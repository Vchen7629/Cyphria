from src.core.settings_config import Settings
import numpy as np


def assign_is_top_pick(ranks: np.ndarray) -> np.ndarray:
    """
    Assign top pick batch to products with rank 1

    Args:
        ranks: Numpy array of integer ranks (1-indexed)

    Returns:
        Numpy array of booleans (True for rank 1)
    """
    return ranks == 1


def assign_is_most_discussed(mention_counts: np.ndarray) -> np.ndarray:
    """
    Assign most discussed badge to products with highest mention count

    Args:
        mention_counts: Numpy array of mention counts

    Returns:
        Numpy array of booleans (True for highest mention count)
    """
    if len(mention_counts) == 0:
        return np.array([], dtype=bool)

    max_count = np.max(mention_counts)
    return mention_counts == max_count


def assign_has_limited_data(mention_counts: np.ndarray, threshold: int | None = None) -> np.ndarray:
    """
    Assign limited data badge to products below a mention threshold

    Args:
        mention_counts: Numpy array of mention counts
        threshold: Minimum mention threshold. If none, uses bayesian params from settings

    Returns:
        Numpy array of booleans (True if mention_count < threshold)
    """
    if threshold is None:
        settings = Settings()
        threshold = settings.BAYESIAN_PARAMS

    return mention_counts < threshold
