from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from ..components.load_data import load_data
from ..components.evaluate import evaluate
from ..components.output_misclassified import misclassified
from ..components.split_dataset import split_dataset
from ..components.save_model import save_model
import pandas as pd
import os
import time


class XgBoostModel:
    def __init__(
        self,
    ) -> None:
        self.label_encoder = LabelEncoder()
        self.XGBoost = XGBClassifier(
            n_estimators=300,
            max_depth=3,
            learning_rate=0.1,
            objective="multi:softmax",
            device="cpu"
        )
        
        self.model = SentenceTransformer(
            "all-MiniLM-L12-v2",
            device="cuda",
        )

    def run(self, file_path: str):
        enc_labels, enc_corpus, corpus, labels = load_data(filepath=file_path, label_encoder=self.label_encoder, embeddings_model=self.model)

        train_x, train_y, test_x, test_y, test_id = split_dataset(encoded_corpus=enc_corpus, encoded_labels=enc_labels, labels=labels)

        trained_model = self.XGBoost.fit(train_x, train_y)

        y_pred_labels, y_test_labels = evaluate(
                                model=self.XGBoost, 
                                label_encoder=self.label_encoder, 
                                encoded_labels=enc_labels, 
                                labels=labels, 
                                x_test=test_x, 
                                y_test=test_y
                            )

        #misclassified(corpus=corpus, y_pred_labels=y_pred_labels, y_test_labels=y_test_labels ,test_id=test_id)

        save_model(model=trained_model, label_encoder=self.label_encoder)


def check_categories(csv_path: str):
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    if "category" not in df.columns:
        print("❌ The CSV does not contain a 'category' column.")
        print(f"Columns found: {list(df.columns)}")
        return

    # Clean category values
    df["category"] = df["category"].astype(str).str.strip().str.strip('"')

    # Count unique values
    category_counts = df["category"].value_counts().sort_index()

    print("✅ Category counts:")
    for category, count in category_counts.items():
        print(f"  {category}: {count}")

    print(f"\nTotal unique categories: {df['category'].nunique()}")
    print(f"Total rows: {len(df)}")

    # Optional check for one-class issue
    if df["category"].nunique() < 2:
        print("\n⚠️ Warning: Only one category found!")
        print("Training will fail with stratification or classification metrics that require multiple classes.")
    else:
        print("\n✅ Multiple categories found — safe to train.")


if __name__ == "__main__":
    start = time.time()
    model = XgBoostModel()
    current_dir = os.path.dirname(__file__)
    data_paths = os.path.join(current_dir, "..", "data", "featureEng.csv")
    data_path = os.path.abspath(data_paths)
    #check_categories(data_path)
    model.run(data_path)

    finish = time.time()
    print("training took:", finish - start, "seconds")
