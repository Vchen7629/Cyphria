import numpy as np
from src.calculation_utils.badge import assign_is_top_pick

def test_assign_rank_one_in_list_unsorted() -> None:
    """Rank 1 in numpy list should be assigned as true in an unsorted numpy array"""
    ranks = np.array([3, 7, 2, 1, 4, 6, 5])

    assert assign_is_top_pick(ranks)[3] == True
    assert assign_is_top_pick(ranks)[0] == False
    assert len(assign_is_top_pick(ranks)) == 7 

def test_no_rank_one_in_list() -> None:
    """Rank list with no rank 1 should be outputted as a list with no True"""
    ranks = np.array([3, 2, 4, 5])

    assert assign_is_top_pick(ranks)[0] == False
    assert assign_is_top_pick(ranks)[1] == False
    assert assign_is_top_pick(ranks)[2] == False
    assert assign_is_top_pick(ranks)[3] == False
    assert len(assign_is_top_pick(ranks)) == 4

def test_empty_input_list() -> None:
    """Empty rank list should be handled properly"""
    assert len(assign_is_top_pick(np.array([]))) == 0

def test_input_output_numpy_same_shape() -> None:
    """Input and output numpy array should be the same shape"""
    ranks = np.array([3, 2, 4, 5])

    assert assign_is_top_pick(ranks).shape == ranks.shape