from xgboost import XGBClassifier
import joblib  # type: ignore
import os
from sklearn.preprocessing import LabelEncoder  # type: ignore


def save_model(model: XGBClassifier, label_encoder: LabelEncoder) -> None:
    folder = os.path.join(os.path.dirname(__file__), "..", "..", "model")
    os.makedirs(folder, exist_ok=True)

    model_path = os.path.join(folder, "xgboost_model.json")
    encoder_path = os.path.join(folder, "label_encoder.joblib")

    model.save_model(model_path)
    joblib.dump(label_encoder, encoder_path)
