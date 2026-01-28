import os

os.environ.setdefault("BAYESIAN_PARAMS", "10")
import numpy as np
from src.calculation_utils.grading import assign_grades


def test_assign_one_rank() -> None:
    """One bayesian score of 0.91 should be assign a value of A"""
    bayesian_scores = np.array([0.91])

    assert assign_grades(bayesian_scores)[0] == "A"


def test_assign_multiple_ranks() -> None:
    """Multiple bayesian scores should be correctly graded"""
    bayesian_scores = np.array([0.91, 0.81, 0.31])

    assert assign_grades(bayesian_scores)[0] == "A"
    assert assign_grades(bayesian_scores)[1] == "B-"
    assert assign_grades(bayesian_scores)[2] == "C-"


def test_assign_boundary_score() -> None:
    """Boundary bayesian score like 0.9 for A should be assigned A"""
    bayesian_scores = np.array([0.90])

    assert assign_grades(bayesian_scores)[0] == "A"


def test_max_negative_score() -> None:
    """Max negative score (-1.0) should be assigned F-"""
    bayesian_scores = np.array([-1.0])

    assert assign_grades(bayesian_scores)[0] == "F-"


def test_max_positive_score() -> None:
    """Max positive score (1.0) should be assigned S"""
    bayesian_scores = np.array([1.0])

    assert assign_grades(bayesian_scores)[0] == "S"


def test_no_bayesian_score() -> None:
    """No bayesian score should not assign anything"""
    bayesian_scores = np.array([])

    assert len(assign_grades(bayesian_scores)) == 0
