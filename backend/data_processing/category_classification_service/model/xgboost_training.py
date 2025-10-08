from sentence_transformers import (
    SentenceTransformer,
)
from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV
)
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
)
from sklearn.preprocessing import (
    LabelEncoder,
)
from xgboost import (
    XGBClassifier,
)
import pandas as pd
import numpy as np
import os, time, csv


class XgBoostModel:
    def __init__(
        self,
    ) -> None:
        self.label_encoder = LabelEncoder()
        self.XGBoost = XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.1,
            objective="multi:softmax",
        )
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            device="cpu",
        )

        #self.params = {
        #    "n_estimators": [100, 200, 300],
        #    "max_depth": [1, 3, 5, 7],
        #    "learning_rate": [0.01, 0.1, 0.2, 0.3],
        #}

    def loadData(
        self,
        filepath: str,
    ) -> None:
        df = pd.read_csv(filepath)
        missing_category_rows = df[df["category"].isna() | (df["category"].str.strip() == "")]

        if not missing_category_rows.empty:
            print("Rows with missing 'category':")
            print(missing_category_rows)

        self.corpus = df["post"].tolist()
        self.labels = [label.strip().strip('"') for label in df["category"].tolist()]

        self.xgboost_labels = self.label_encoder.fit_transform(self.labels)
        self.x = self.model.encode(self.corpus)

    def train(
        self,
    ) -> None:
        indicies = np.arange(len(self.x))
        (
            train_x,
            test_x,
            train_y,
            test_y,
            train_id,
            test_id,
        ) = train_test_split(
            self.x,
            self.xgboost_labels,
            indicies,
            test_size=0.3,
            random_state=42,
            stratify=self.labels,
        )

        #self.rs = RandomizedSearchCV(
        #    estimator=self.XGBoost,
        #    param_distributions=self.params,
        #    n_iter=20, # number of times the randomized search runs to find best hyperparams
       #     cv=5, # 5 fold cross valid
        #    scoring="accuracy",
        #    random_state=42,
        #    n_jobs=-1, # number of cpu cores used, -1 means all
        #) 

        #self.rs.fit(
        #    train_x,
        #    train_y,
        #)

        self.XGBoost.fit(
            train_x,
            train_y,
        )

        self.X_test = test_x
        self.Y_test = test_y
        self.test_id = test_id

    def evaluate(
        self,
    ) -> None:
        #best_model = self.rs.best_estimator_
        xgboost_y_pred = self.XGBoost.predict(self.X_test)
        xgboost_y_score = self.XGBoost.predict_proba(self.X_test)
        self.xgboost_y_pred_labels = self.label_encoder.inverse_transform(xgboost_y_pred)
        self.y_test_labels = self.label_encoder.inverse_transform(self.Y_test)

        xgboost_correct = 0
        for i in range(len(xgboost_y_pred)):
            if xgboost_y_pred[i] == self.Y_test[i]:
                xgboost_correct += 1

        print(set(self.labels))
        print(set(self.label_encoder.inverse_transform(self.xgboost_labels)))

        print("XGBoost Classification Report:")
        print(
            classification_report(
                self.y_test_labels,
                self.xgboost_y_pred_labels,
            )
        )

        roc_auc_ovo = roc_auc_score(
            self.Y_test,
            xgboost_y_score,
            labels=list(range(len(self.label_encoder.classes_))),
            multi_class="ovo",
            average="macro",
        )
        print("AUC ROC Score for XGBoost OVO: %.2f%%" % roc_auc_ovo)

        print(
            "Accuracy of XGBOOST machine model with simple train test split: %.2f%%"
            % (xgboost_correct / float(len(xgboost_y_pred)) * 100)
        )
        
        #print("Best params:", self.rs.best_params_)
        #print("Best CV score:", self.rs.best_score_)

        # using the best model found by RandomizedSearchCV on test data set
        #print("Test accuracy:", best_model.score(self.X_test, self.Y_test))
    def misclassified(
        self,
    ) -> None:
        header = [
            "post",
            "predicted_category",
            "actual_category",
        ]

        file_name = "misclassified_posts.csv"
        target_dir = os.path.join(
            os.path.dirname(__file__),
            "..",
            "datasets",
        )
        filepath = os.path.join(
            target_dir,
            file_name,
        )
        file_exists = os.path.isfile(filepath)

        try:
            os.makedirs(
                target_dir,
                exist_ok=True,
            )
        except Exception as e:
            print(f"Error creating directory: {e}")
            return
        else:
            with open(
                filepath,
                "w",
                newline="",
                encoding="utf-8",
            ) as file:
                writer = csv.writer(
                    file,
                    quoting=csv.QUOTE_ALL,
                )
                if not file_exists:
                    writer.writerow(header)
                test_posts = [self.corpus[i] for i in self.test_id]
                for i in range(len(self.xgboost_y_pred_labels)):
                    if self.xgboost_y_pred_labels[i] != self.y_test_labels[i]:
                        writer.writerow(
                            [
                                test_posts[i],
                                self.xgboost_y_pred_labels[i],
                                self.y_test_labels[i],
                            ]
                        )


if __name__ == "__main__":
    start = time.time()
    model = XgBoostModel()

    model.loadData("../datasets/featureEng.csv")
    model.train()
    model.evaluate()
    model.misclassified()
    finish = time.time()
    print(
        "training took:",
        finish - start,
        "seconds",
    )
