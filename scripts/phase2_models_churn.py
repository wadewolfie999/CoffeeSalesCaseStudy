import pandas as pd
import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
from utils import ensure_dir, save_csv
from config import PATHS

def train_logistic_regression(X: pd.DataFrame, y: pd.Series) -> LogisticRegression:
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    return model

def train_random_forest(X: pd.DataFrame, y: pd.Series, n_estimators=100, random_state=42) -> RandomForestClassifier:
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
    model.fit(X, y)
    return model

def predict(model, X: pd.DataFrame) -> pd.Series:
    return pd.Series(model.predict(X), index=X.index)

def evaluate_classification(y_true: pd.Series, y_pred: pd.Series) -> dict:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "roc_auc": roc_auc_score(y_true, y_pred),
        "f1_score": f1_score(y_true, y_pred)
    }

def save_model(model, filename: str):
    ensure_dir(PATHS["models"])
    path = os.path.join(PATHS["models"], filename)
    joblib.dump(model, path)
    return path

def export_predictions(preds: pd.Series, filename: str = "churn_predictions.csv"):
    ensure_dir(PATHS["models"])
    out_path = os.path.join(PATHS["models"], filename)
    save_csv(preds.to_frame(name="churn_prediction"), out_path)

if __name__ == "__main__":
    X = pd.read_csv(PATHS["features"])
    y = pd.read_csv(PATHS["phase1_clean"])["churn_flag"]

    lr_model = train_logistic_regression(X, y)
    rf_model = train_random_forest(X, y)

    lr_preds = predict(lr_model, X)
    rf_preds = predict(rf_model, X)

    export_predictions(lr_preds, "lr_churn_predictions.csv")
    export_predictions(rf_preds, "rf_churn_predictions.csv")

    print("Churn models trained and predictions exported.")
