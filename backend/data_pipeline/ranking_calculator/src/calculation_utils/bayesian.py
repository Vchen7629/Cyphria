import numpy as np


def calculate_bayesian_scores(
    avg_sentiments: np.ndarray, mention_counts: np.ndarray, min_mentions: int = 10
) -> np.ndarray:
    """
    Calculate Bayesian weighted scores using the IMDB Top 250 formula.

    Formula: WR = (v / (v + m)) × R + (m / (v + m)) × C

    Where:
        WR = Weighted Rating (Bayesian score)
        R  = Average sentiment for this product
        v  = Mention count for this product
        m  = Minimum mentions threshold
        C  = Mean sentiment across all products in category (weighted by mentions)

    used to preventing manipulation from low-sample products since Products with
    few mentions get pulled toward the category average,.

    Args:
        avg_sentiments: Array of average sentiment scores per product
        mention_counts: Array of mention counts per product
        min_mentions: Minimum mentions threshold (m in formula)

    Returns:
        Array of Bayesian weighted scores
    """
    category_mean = np.average(avg_sentiments, weights=mention_counts)

    # WR = (v / (v + m)) × R + (m / (v + m)) × C
    weight = mention_counts / (mention_counts + min_mentions)
    bayesian_scores = weight * avg_sentiments + (1 - weight) * category_mean

    return bayesian_scores
