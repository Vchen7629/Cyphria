import numpy as np
from src.calculation_utils.grading import assign_grades
from src.calculation_utils.grading import assign_ranks
import pytest


@pytest.mark.parametrize(
    argnames="score,expected", argvalues=[(0.91, "A"), (0.90, "A"), (-1.0, "F-"), (1.0, "S")]
)
def test_assign_one_rank(score: int, expected: str) -> None:
    """Testing multiple cases including boundary cases"""
    bayesian_scores = np.array([score])

    assert assign_grades(bayesian_scores)[0] == expected


def test_assign_multiple_ranks() -> None:
    """Multiple bayesian scores should be correctly graded"""
    bayesian_scores = np.array([0.91, 0.81, 0.31])

    assert assign_grades(bayesian_scores)[0] == "A"
    assert assign_grades(bayesian_scores)[1] == "B-"
    assert assign_grades(bayesian_scores)[2] == "C-"


def test_no_bayesian_score() -> None:
    """No bayesian score should not assign anything"""
    bayesian_scores = np.array([])

    assert len(assign_grades(bayesian_scores)) == 0


def test_assign_ranks() -> None:
    """Each score should be assigned the correct rank based on its value (highest score = rank 1)"""
    bayesian_scores = np.array([0.31, 0.91, 0.21, 0.55])

    ranks = assign_ranks(bayesian_scores)
    assert ranks[0] == 3  # 0.31 is 3rd highest
    assert ranks[1] == 1  # 0.91 is highest
    assert ranks[2] == 4  # 0.21 is lowest
    assert ranks[3] == 2  # 0.55 is 2nd highest


def test_assign_empty_scores() -> None:
    """Empty input score list shouldnt be assigned any ranks"""
    assert len(assign_ranks(np.array([]))) == 0


def test_multiple_scores_same_value() -> None:
    """Multiple bayesian scores with the same score should be handled"""
    bayesian_scores = np.array([0.31, 0.91, 0.91, 0.31])

    ranks = assign_ranks(bayesian_scores)
    assert ranks[0] == 3
    assert ranks[1] == 1
    assert ranks[2] == 1
    assert ranks[3] == 3


def test_single_score() -> None:
    """Single score should get rank 1"""
    assert assign_ranks(np.array([0.99]))[0] == 1


def test_scores_with_positive_negative() -> None:
    """Negatives should be ranked lower than positive"""
    bayesian_scores = np.array([0.31, 0.91, -0.21])

    ranks = assign_ranks(bayesian_scores)
    assert ranks[0] == 2
    assert ranks[1] == 1
    assert ranks[2] == 3
