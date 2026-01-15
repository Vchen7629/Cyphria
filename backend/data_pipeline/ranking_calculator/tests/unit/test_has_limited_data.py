import numpy as np
import os

os.environ.setdefault("PRODUCT_CATEGORY", "GPU")
os.environ.setdefault("TIME_WINDOWS", "all_time")
os.environ.setdefault("BAYESIAN_PARAMS", "10")

from src.calculation_utils.badge import assign_has_limited_data

def test_assigns_badge_unsorted_list() -> None:
    """A value below the threshold in unsorted input numpy array should be set to true"""
    mention_counts = np.array([33, 2, 17, 99, 55])

    assign = assign_has_limited_data(mention_counts, threshold=10)

    assert assign[0] == False
    assert assign[1] == True
    assert assign[2] == False
    assert assign[3] == False
    assert assign[4] == False
    assert len(assign) == 5

def test_mention_same_as_threshold() -> None:
    """Mention counts same as threshold should be set as false"""
    mention_counts = np.array([10, 33, 22])

    assign = assign_has_limited_data(mention_counts, threshold=10)

    assert assign[0] == False
    assert assign[1] == False
    assert assign[2] == False
    assert len(assign) == 3

def test_no_mentions() -> None:
    """Empty mentions list should be handled"""
    assert len(assign_has_limited_data(np.array([]))) == 0

def test_input_output_same_shape() -> None:
    """Input and output numpy array should have the same shape"""
    mention_counts = np.array([10, 32, 22])

    result = assign_has_limited_data(mention_counts, threshold=10)
    assert result.shape == mention_counts.shape

def test_multiple_mentions_below_threshold() -> None:
    """Multiple mention counts below threshold should all be marked as True"""
    mention_counts = np.array([9, 3, 33, 55])

    result = assign_has_limited_data(mention_counts, threshold=10)

    assert result[0] == True
    assert result[1] == True
    assert result[2] == False
    assert result[3] == False
    assert len(result) == 4