import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sentence_transformers import SentenceTransformer



# Helper Function to Load Training Data Set
def load_data(filepath: str, label_encoder: LabelEncoder, embeddings_model: SentenceTransformer) -> None:
    df = pd.read_csv(filepath)
    missing_category_rows = df[df["category"].isna() | (df["category"].str.strip() == "")]

    if not missing_category_rows.empty:
        print("Rows with missing 'category':")
        print(missing_category_rows)

    corpus = df["post"].tolist()
    labels = [label.strip().strip('"') for label in df["category"].tolist()]

    encoded_labels = label_encoder.fit_transform(labels)
    #print("Loaded CSV shape:", df.shape)
    #print("Columns:", df.columns.tolist())
    #print(df.head())
    encoded_corpus = embeddings_model.encode(corpus)

    return encoded_labels, encoded_corpus, corpus, labels
