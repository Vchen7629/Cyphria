from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV  # type: ignore
import numpy as np


# Use RandomizedSearchCV to do grid Search + K-fold Cross Validation to find best parameters
def hyperparam_tuning(model: XGBClassifier, train_x: np.ndarray, train_y: np.ndarray) -> None:
    params = {
        "n_estimators": [100, 200, 300],
        "max_depth": [1, 3, 5, 7],
        "learning_rate": [0.01, 0.1, 0.2, 0.3],
    }

    rs = RandomizedSearchCV(
        estimator=model,
        param_distributions=params,
        n_iter=20,  # number of times the randomized search runs to find best hyperparams
        cv=5,  # 5 fold cross valid
        scoring="accuracy",
        random_state=42,
        n_jobs=-1,  # number of cpu cores used, -1 means all
    )

    rs.fit(train_x, train_y)
