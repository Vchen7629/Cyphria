from src.core.settings_config import Settings
import numpy as np
from scipy.stats import rankdata

def assign_grades(bayesian_scores: np.ndarray) -> np.ndarray:
    """
    Convert Bayesian scores to letter grades

    Grading Scale (from -1 to +1):
        S: >= 0.95
        A: >= 0.9
        A-: >= 0.85
        B: >= 0.75
        B-: >= 0.7
        C: >= 0.45
        C-: >= 0.1
        D: >= -0.1
        D-: >= -0.3
        F: >= -0.5
        F-: >= -1.0
    Args:
        bayesian_scores: Numpy array of Bayesian weighted scores
    
    Returns:
        Numpy array of letter grade strings
    """
    settings = Settings()

    indicies = np.searchsorted(-settings.GRADE_THRESHOLDS, -bayesian_scores, side="left")
    return settings.GRADE_VALUES[indicies]

def assign_ranks(bayesian_scores: np.ndarray) -> np.ndarray:
    """
    Assign ranks based on bayesian scores (highest score = rank 1)
    
    Args:
        bayesian_scores: numpy array of bayesian weighted scores
    
    Returns:
        numpy array of integer ranks (1-indexed)
    """
    return rankdata(-bayesian_scores, method="min").astype(int)