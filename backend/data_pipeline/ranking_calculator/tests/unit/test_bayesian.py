import numpy as np
import pytest
from src.calculation_utils.bayesian import calculate_bayesian_scores

def test_single_product_equals_own_score() -> None:
    """Single product bayesian score should equal its avg sentiment"""
    avg_sentiments = np.array([0.5])
    mention_counts = np.array([100])

    scores = calculate_bayesian_scores(avg_sentiments, mention_counts)

    assert scores[0] == 0.5

def test_high_mentions_stays_close_to_actual() -> None:
    """Product with many mentions should stay close to its actual score"""
    avg_sentiments = np.array([0.8, 0.2])
    mention_counts = np.array([1000, 1000])

    scores = calculate_bayesian_scores(avg_sentiments, mention_counts)

    assert scores[0] == pytest.approx(0.8, abs=0.01)
    assert scores[1] == pytest.approx(0.2, abs=0.01)

def test_low_mentions_pulled_toward_category_mean() -> None:
    """Product with few mentions should be pulled toward category mean"""
    avg_sentiments = np.array([0.9, 0.1])
    mention_counts = np.array([1, 1000])

    scores = calculate_bayesian_scores(avg_sentiments, mention_counts)

    assert scores[0] < 0.5
    assert scores[1] == pytest.approx(0.1, abs=0.02)

def test_zero_mentions_returns_category_mean() -> None:
    """Product with zero mentions should get category mean"""
    avg_sentiments = np.array([0.8, 0.4])
    mention_counts = np.array([0, 100])

    scores = calculate_bayesian_scores(avg_sentiments, mention_counts)

    # Category mean is 0.4 since only second product contributes
    assert scores[0] == 0.4

def test_negative_sentiments() -> None:
    """Negative sentiment scores should be correctly handled"""
    avg_sentiments = np.array([-0.5, 0.5])
    mention_counts = np.array([100, 100])

    scores = calculate_bayesian_scores(avg_sentiments, mention_counts)

    assert scores[0] < 0
    assert scores[1] > 0

def test_min_mentions_parameter() -> None:
    """Higher min mentions pulls scores toward category mean"""
    avg_sentiments = np.array([0.8, 0.2])
    mention_counts = np.array([50, 50])

    scores_low_m = calculate_bayesian_scores(avg_sentiments, mention_counts, min_mentions=10)
    scores_high_m = calculate_bayesian_scores(avg_sentiments, mention_counts, min_mentions=100)

    assert abs(scores_high_m[0] - 0.5) < abs(scores_low_m[0] - 0.5)
    assert abs(scores_high_m[1] - 0.5) < abs(scores_low_m[1] - 0.5)

def test_output_shape_matches_input() -> None:
    """Output numpy array should have same shape as input"""
    avg_sentiments = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    mention_counts = np.array([10, 20, 30, 40, 50])

    scores = calculate_bayesian_scores(avg_sentiments, mention_counts)

    assert scores.shape == avg_sentiments.shape

def test_scores_bounded_by_extremes() -> None:
    """Bayesian scores stay within the range (low, high) of input sentiments"""
    avg_sentiments = np.array([0.2, 0.5, 0.8])
    mention_counts = np.array([10, 50, 100])

    scores = calculate_bayesian_scores(avg_sentiments, mention_counts)

    assert all(scores >= 0.2)
    assert all(scores <= 0.8)