import os
import json
import pandas as pd
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV, train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
import shap
import matplotlib.pyplot as plt

from config import PATHS_OPT as PATHS
from utils import ensure_dir, save_csv, safe_save_plot

MODEL_DIR = PATHS["models"]
HYPERPARAMS_FILE = os.path.join(MODEL_DIR, "hyperparams_rf.json")
LR_MODEL_FILE = os.path.join(MODEL_DIR, "lr_churn.joblib")
RF_MODEL_FILE = os.path.join(MODEL_DIR, "rf_churn.joblib")
SHAP_SUMMARY_FILE = os.path.join(PATHS["logs"], "shap_summary.png")
PRED_CSV_LR = os.path.join(MODEL_DIR, "lr_churn_predictions.csv")
PRED_CSV_RF = os.path.join(MODEL_DIR, "rf_churn_predictions.csv")

def train_logistic_regression(X: pd.DataFrame, y: pd.Series) -> LogisticRegression:
    model = LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear")
    model.fit(X, y)
    ensure_dir(MODEL_DIR)
    joblib.dump(model, LR_MODEL_FILE)
    return model

def tune_random_forest(X: pd.DataFrame, y: pd.Series, cv_splits: int = 3) -> RandomForestClassifier:
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [6, 10, None],
        "min_samples_split": [2, 5]
    }
    cv = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=42)
    gs = GridSearchCV(RandomForestClassifier(class_weight="balanced", random_state=42),
                      param_grid, cv=cv, scoring="roc_auc", n_jobs=-1)
    gs.fit(X, y)
    ensure_dir(MODEL_DIR)
    with open(HYPERPARAMS_FILE, "w") as f:
        json.dump(gs.best_params_, f, indent=2)
    joblib.dump(gs.best_estimator_, RF_MODEL_FILE)
    return gs.best_estimator_

def train_random_forest(X: pd.DataFrame, y: pd.Series, n_estimators: int = 200) -> RandomForestClassifier:
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=42, class_weight="balanced")
    model.fit(X, y)
    ensure_dir(MODEL_DIR)
    joblib.dump(model, RF_MODEL_FILE)
    return model

def predict(model, X: pd.DataFrame) -> pd.Series:
    preds = model.predict(X)
    return pd.Series(preds, index=X.index)

def predict_proba(model, X: pd.DataFrame) -> pd.Series:
    if hasattr(model, "predict_proba"):
        return pd.Series(model.predict_proba(X)[:, 1], index=X.index)
    # fallback for linear models with decision function
    return pd.Series(model.decision_function(X), index=X.index)

def evaluate(y_true: pd.Series, y_pred: pd.Series) -> dict:
    y_t = np.array(y_true)
    y_p = np.array(y_pred)
    res = {
        "accuracy": float(accuracy_score(y_t, y_p)),
        "roc_auc": float(roc_auc_score(y_t, y_p)),
        "f1": float(f1_score(y_t, y_p))
    }
    return res

def export_predictions(preds: pd.Series, filename: str):
    ensure_dir(MODEL_DIR)
    save_csv(pd.DataFrame({"prediction": preds}), os.path.join(MODEL_DIR, filename))

def log_shap(model, X: pd.DataFrame, out_path: str = SHAP_SUMMARY_FILE):
    # SHAP for tree models uses TreeExplainer; for linear, KernelExplainer fallback
    ensure_dir(PATHS["logs"])
    explainer = shap.TreeExplainer(model) if hasattr(shap, "TreeExplainer") else shap.KernelExplainer(model.predict, X.iloc[:50,:])
    shap_values = explainer.shap_values(X)
    plt.figure(figsize=(8,6))
    # TreeExplainer shap_values for binary classifier returns list [neg, pos]; choose pos if list
    vals = shap_values[1] if isinstance(shap_values, list) else shap_values
    shap.summary_plot(vals, X, show=False)
    fig = plt.gcf()
    safe_save_plot(fig, out_path)
    plt.close(fig)

if __name__ == "__main__":
    # Load features and target
    feats_path = os.path.join(PATHS["features"], "features.csv")
    df = pd.read_csv(feats_path, parse_dates=["transaction_date"])
    # choose columns for modeling
    # exclude identifiers and target if present; adapt to your feature columns
    drop_cols = ["transaction_id", "product_id", "product_category", "transaction_date", "store_location"]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore").fillna(0)
    # target must be present in phase1 clean or features: 'churn_flag'
    y = pd.read_csv(PATHS["phase1_clean"])["churn_flag"]
    # align lengths if needed
    if len(y) != len(X):
        y = y.iloc[:len(X)].reset_index(drop=True)
        X = X.reset_index(drop=True).iloc[:len(y)]

    # split for quick local tuning
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

    lr = train_logistic_regression(X_train, y_train)
    rf = tune_random_forest(X_train, y_train, cv_splits=3)

    lr_preds = predict(lr, X_test)
    rf_preds = predict(rf, X_test)

    lr_metrics = evaluate(y_test, lr_preds)
    rf_metrics = evaluate(y_test, rf_preds)

    # export
    export_predictions(pd.Series(lr_preds, index=X_test.index), "lr_churn_predictions.csv")
    export_predictions(pd.Series(rf_preds, index=X_test.index), "rf_churn_predictions.csv")
    # log shap for rf
    try:
        log_shap(rf, X_train)
    except Exception:
        pass

    print("Churn training complete. Metrics:")
    print("LR:", lr_metrics)
    print("RF:", rf_metrics)
