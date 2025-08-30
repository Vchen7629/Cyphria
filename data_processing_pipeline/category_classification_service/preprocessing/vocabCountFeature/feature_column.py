import scipy.sparse as sp
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from vocabCountFeature import vocab_list

# This function Creates the columns that contain the category score using tfidf and a preset vocab
def categoryScores(features: sp.csr_matrix, tfidf_vocab: dict[str, int], combined_vocab: dict[str, list[str]]) -> list[sp.csr_matrix]:
    category_columns = []

    for _, category_vocab in combined_vocab.items():
        category_vocab = [w.lower() for w in category_vocab]
        idx_list = vocab_list.constructor(tfidf_vocab, category_vocab)

        if idx_list:
            # select all posts or rows where 
            score = features[:, idx_list].sum(axis=1)
            category_score = sp.csr_matrix(score).reshape(-1, 1)
        else:
            category_score = sp.csr_matrix((features.shape[0], 1))

        #print(f"Words in vocab: {category_vocab}")
        #print(f"TFIDF vocab overlap: {[w for w in category_vocab if w in tfidf_vocab]}")
        category_columns.append(category_score)
        
    return category_columns

# This function Combines the newly created Category Scores with the
# Tf-IDF Matrix into one matrix to be used for the model
def combine(category_columns: list[sp.csr_matrix], X_tfidf: sp.csr_matrix):
    combined_cat_scores = sp.hstack(category_columns, format="csr")
    print("Non-zero entries in combined feature matrix:", combined_cat_scores.nnz)

    # stack the X tf-idf with the combined cat score into one
    x_augmented = sp.hstack([X_tfidf, combined_cat_scores], format = "csr")

    return x_augmented

