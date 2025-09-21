from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2, mutual_info_classif, f_classif
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import pandas as pd
import os, sys, time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing_files.vocabCountFeature import feature_column, loader

class XgBoostModel:
    def __init__(self) -> None:
        token_pattern = r'(?u)\[?\b\w[\w\’\'\-]*\b\]?'
        self.label_encoder = LabelEncoder()
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3),token_pattern=token_pattern, min_df=1) 
        self.XGBoost = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.2, objective="multi:softmax")
    
    def loadData(self, filepath: str) -> None:
        df = pd.read_csv(filepath)
        missing_category_rows = df[df['category'].isna() | (df['category'].str.strip() == '')]

        if not missing_category_rows.empty:
            print("Rows with missing 'category':")
            print(missing_category_rows)

        self.corpus = df['post'].tolist()
        self.labels = [label.strip().strip('"') for label in df['category'].tolist()]

        self.xgboost_labels = self.label_encoder.fit_transform(self.labels)
    
    def _loadVocab(self, folder_name: str) -> dict[str, list[str]]:
        return loader.VocabCoordinator(folder_name).vocabDictBuilder()

    def preprocess(self):
        vocab = self._loadVocab("lexicon_datasets")
        X_tfidf = self.vectorizer.fit_transform(self.corpus)
        tf_idf_vocab = self.vectorizer.vocabulary_

        category_scores = feature_column.categoryScores(X_tfidf, tf_idf_vocab, vocab)
        combine_new_features = feature_column.combine(category_scores, X_tfidf)

        return combine_new_features
        #y = self.labels

        #Eselector = SelectKBest(chi2, k=5400)
        #self.features = selector.fit_transform(X_tfidf, y)


        #self.features = self.vectorizer.fit_transform(self.corpus)

    def train(self) -> None:
        features = self.preprocess()

        train_x, test_x, train_y, test_y = train_test_split(
            features, self.xgboost_labels, test_size=0.3, random_state=42, stratify=self.labels)

        self.XGBoost.fit(train_x, train_y)
        self.X_test = test_x
        self.Y_test = test_y

    def evaluate(self) -> None:
        xgboost_y_pred = self.XGBoost.predict(self.X_test)
        xgboost_y_score = self.XGBoost.predict_proba(self.X_test)
        xgboost_y_pred_labels = self.label_encoder.inverse_transform(xgboost_y_pred)
        y_test_labels = self.label_encoder.inverse_transform(self.Y_test)
        
        xgboost_correct = 0
        for i in range(len(xgboost_y_pred)):
            if xgboost_y_pred[i] == self.Y_test[i]:
                xgboost_correct += 1

        print(set(self.labels))
        print(set(self.label_encoder.inverse_transform(self.xgboost_labels)))

        print("XGBoost Classification Report:")
        print(classification_report(y_test_labels, xgboost_y_pred_labels))

        roc_auc_ovo = roc_auc_score(self.Y_test, xgboost_y_score, labels=list(range(len(self.label_encoder.classes_))), multi_class='ovo', average='macro')
        print("AUC ROC Score for XGBoost OVO: %.2f%%" % roc_auc_ovo)
        
        print("Accuracy of XGBOOST machine model: %.2f%%" % ((xgboost_correct / float(len(xgboost_y_pred)) * 100)))
    
    def misclassified(self) -> None:
        print("Misclassified Posts:")

        #test_posts = [for ]

if __name__ == "__main__":
    start = time.time()
    model = XgBoostModel()

    model.loadData("../datasets/featureEng.csv")
    model.preprocess()
    model.train()
    model.evaluate()
    finish = time.time()
    print("training took:", finish - start, "seconds")