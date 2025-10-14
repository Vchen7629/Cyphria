from sklearn.metrics import (
    classification_report,
    roc_auc_score,
)

def evaluate(model, label_encoder, encoded_labels, labels, x_test, y_test) -> None:
        #best_model = self.rs.best_estimator_
        xgboost_y_pred = model.predict(x_test)
        xgboost_y_score = model.predict_proba(x_test)
        y_pred_labels = label_encoder.inverse_transform(xgboost_y_pred)
        y_test_labels = label_encoder.inverse_transform(y_test)

        xgboost_correct = 0
        for i in range(len(xgboost_y_pred)):
            if xgboost_y_pred[i] == y_test[i]:
                xgboost_correct += 1

        print(set(labels))
        print(set(label_encoder.inverse_transform(encoded_labels)))

        print("XGBoost Classification Report:")
        print(
            classification_report(
                y_test_labels,
                y_pred_labels,
            )
        )

        roc_auc_ovo = roc_auc_score(
            y_test,
            xgboost_y_score,
            labels=list(range(len(label_encoder.classes_))),
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

        return y_pred_labels, y_test_labels