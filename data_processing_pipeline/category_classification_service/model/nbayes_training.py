from sklearn.feature_extraction.text import (
    TfidfVectorizer,
)
from sklearn.naive_bayes import (
    MultinomialNB,
)
from sklearn.svm import (
    SVC,
)
from sklearn.feature_selection import (
    SelectKBest,
    chi2,
)
from sklearn.model_selection import (
    train_test_split,
)
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
)
from sklearn.preprocessing import (
    LabelEncoder,
)
import pandas as pd


class MultimodalNaiveBayesModel:
    def __init__(
        self,
    ):
        token_pattern = r"(?u)\[?\b\w[\w\’\'\-]*\b\]?"
        self.label_encoder = LabelEncoder()
        self.NBmodel = MultinomialNB()
        self.SVMmodel = SVC(kernel="linear")
        self.vectorizer = TfidfVectorizer(
            ngram_range=(
                1,
                2,
            ),
            token_pattern=token_pattern,
            min_df=3,
        )

    def loadData(
        self,
        filepath: str,
    ):
        df = pd.read_csv(filepath)

        self.corpus = df["post"].tolist()
        self.labels = [label.strip().strip('"') for label in df["category"].tolist()]

    def preprocess(
        self,
    ):
        X = self.vectorizer.fit_transform(self.corpus)
        y = self.labels

        selector = SelectKBest(
            chi2,
            k=5000,
        )

        self.features = selector.fit_transform(
            X,
            y,
        )

    def train(
        self,
    ):
        (
            train_x,
            test_x,
            train_y,
            test_y,
        ) = train_test_split(
            self.features,
            self.labels,
            test_size=0.3,
            random_state=42,
            stratify=self.labels,
        )

        self.NBmodel.fit(
            train_x,
            train_y,
        )
        self.SVMmodel.fit(
            train_x,
            train_y,
        )
        self.X_test = test_x
        self.Y_test = test_y

    def evaluate(
        self,
    ):
        nb_y_pred = self.NBmodel.predict(self.X_test)
        nb_y_score = self.NBmodel.predict_proba(self.X_test)
        svm_y_pred = self.SVMmodel.predict(self.X_test)

        nb_correct = 0
        for i in range(len(nb_y_pred)):
            if nb_y_pred[i] == self.Y_test[i]:
                nb_correct += 1

        svm_correct = 0
        for i in range(len(svm_y_pred)):
            if svm_y_pred[i] == self.Y_test[i]:
                svm_correct += 1

        print("Naive Bayes Classification Report:")
        print(
            classification_report(
                self.Y_test,
                nb_y_pred,
            )
        )

        print("Naive SVC Classification Report:")
        print(
            classification_report(
                self.Y_test,
                svm_y_pred,
            )
        )

        print("Accuracy of naive bayes model: %.2f%%" % (nb_correct / float(len(nb_y_pred)) * 100))
        nb_roc_auc_ovo = roc_auc_score(
            self.Y_test,
            nb_y_score,
            multi_class="ovr",
            average="macro",
        )
        print("AUC ROC Score for Naive Bayes OVO: %.2f%%" % nb_roc_auc_ovo)
        print(
            "Accuracy of support vector machine model: %.2f%%"
            % (svm_correct / float(len(svm_y_pred)) * 100)
        )


if __name__ == "__main__":
    model = MultimodalNaiveBayesModel()

    model.loadData("../datasets/reddit_posts.csv")
    model.preprocess()
    model.train()
    model.evaluate()
