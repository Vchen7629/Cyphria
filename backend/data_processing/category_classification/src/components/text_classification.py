import numpy as np
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder  # type: ignore


def text_classification(
    model: XGBClassifier, label_encoder: LabelEncoder, batch_embeddings: list[np.ndarray]
) -> list[str]:
    # Stack all embeddings into one 2D array for XGBoost
    X_batch = np.vstack(batch_embeddings)

    # predict encoded label
    xgboost_pred = model.predict(X_batch)

    # convert the label to a readable string
    pred_labels = label_encoder.inverse_transform(xgboost_pred)
    label_strings = [str(label) for label in pred_labels]

    return label_strings
