import joblib  # type: ignore
import os
from xgboost import XGBClassifier
from typing import Any


# This function loads the classifier model
def load_model() -> tuple[XGBClassifier, Any]:
    folder = os.path.join(os.path.dirname(__file__), "..", "model")

    model_path = os.path.join(folder, "xgboost_model.json")
    encoder_path = os.path.join(folder, "label_encoder.joblib")

    model = XGBClassifier()
    model.load_model(model_path)

    label_encoder = joblib.load(encoder_path)

    return model, label_encoder
