import xgboost as xgb
import joblib
import os
from sklearn.preprocessing import LabelEncoder

def save_model(model: xgb, label_encoder: LabelEncoder):
    folder = os.path.join(os.path.dirname(__file__), "..", "..", "model")
    os.makedirs(folder, exist_ok=True) 

    model_path = os.path.join(folder, "xgboost_model.json")
    encoder_path = os.path.join(folder, "label_encoder.joblib")

    model.save_model(model_path)
    joblib.dump(label_encoder, encoder_path)