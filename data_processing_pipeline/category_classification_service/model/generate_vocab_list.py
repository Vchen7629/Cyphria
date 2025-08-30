from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def generate_vocab_lists(corpus, labels, top_k=50):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X = vectorizer.fit_transform(corpus)
    tfidf_df = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())
    tfidf_df['label'] = labels

    category_vocab = {}
    for cat in set(labels):
        avg_tfidf = tfidf_df[tfidf_df['label'] == cat].drop(columns=['label']).mean()
        top_terms = avg_tfidf.sort_values(ascending=False).head(top_k).index.tolist()
        category_vocab[cat] = top_terms
    
    return category_vocab