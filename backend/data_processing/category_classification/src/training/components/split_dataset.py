import numpy as np
from sklearn.model_selection import train_test_split  # type: ignore
from typing import Tuple


def split_dataset(
    encoded_corpus: np.ndarray, encoded_labels: np.ndarray, labels: list[str]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    indicies = np.arange(len(encoded_corpus))

    (
        train_x,
        test_x,
        train_y,
        test_y,
        train_id,
        test_id,
    ) = train_test_split(
        encoded_corpus,
        encoded_labels,
        indicies,
        test_size=0.3,
        random_state=42,
        stratify=labels,
    )

    return train_x, train_y, test_x, test_y, test_id
