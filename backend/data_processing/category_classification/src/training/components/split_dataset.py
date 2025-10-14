import numpy as np
from sklearn.model_selection import train_test_split

def split_dataset(encoded_corpus, encoded_labels, labels):
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