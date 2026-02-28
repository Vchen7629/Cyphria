import numpy as np
from src.calculation_utils.badge import assign_is_top_pick
from src.calculation_utils.badge import assign_is_most_discussed


def test_most_discussed_mixed_list() -> None:
    """Most discussed mention count in a mixed (unsorted) numpy list should be set to true"""
    mention_counts = np.array([33, 555, 22, 239, 1])

    assert assign_is_most_discussed(mention_counts)[1]
    assert not assign_is_most_discussed(mention_counts)[0]
    assert not assign_is_most_discussed(mention_counts)[2]
    assert not assign_is_most_discussed(mention_counts)[3]
    assert not assign_is_most_discussed(mention_counts)[4]
    assert len(assign_is_most_discussed(mention_counts)) == 5


def test_empty_mention_count_list() -> None:
    """Empty input numpy list should be handled properly"""
    assert len(assign_is_most_discussed(np.array([]))) == 0


def test_multiple_most_discussed_input() -> None:
    """Multiple mention counts that are the same and are the highest should be marked as true"""
    mention_counts = np.array([33, 999, 999])

    assert not assign_is_most_discussed(mention_counts)[0]
    assert assign_is_most_discussed(mention_counts)[1]
    assert assign_is_most_discussed(mention_counts)[2]


def test_input_output_same_shape() -> None:
    """Input and output numpy arrays should be the same shape"""
    mention_counts = np.array([33, 555, 22, 239, 1])

    assert assign_is_most_discussed(mention_counts).shape == mention_counts.shape


def test_assign_rank_one_in_list_unsorted() -> None:
    """Rank 1 in numpy list should be assigned as true in an unsorted numpy array"""
    ranks = np.array([3, 7, 2, 1, 4, 6, 5])

    assert assign_is_top_pick(ranks)[3]
    assert not assign_is_top_pick(ranks)[0]
    assert len(assign_is_top_pick(ranks)) == 7


def test_no_rank_one_in_list() -> None:
    """Rank list with no rank 1 should be outputted as a list with no True"""
    ranks = np.array([3, 2, 4, 5])

    assert not assign_is_top_pick(ranks)[0]
    assert not assign_is_top_pick(ranks)[1]
    assert not assign_is_top_pick(ranks)[2]
    assert not assign_is_top_pick(ranks)[3]
    assert len(assign_is_top_pick(ranks)) == 4


def test_empty_input_list() -> None:
    """Empty rank list should be handled properly"""
    assert len(assign_is_top_pick(np.array([]))) == 0


def test_input_output_numpy_same_shape() -> None:
    """Input and output numpy array should be the same shape"""
    ranks = np.array([3, 2, 4, 5])

    assert assign_is_top_pick(ranks).shape == ranks.shape
