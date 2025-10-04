import os
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, f1_score, roc_auc_score

from config import PATHS_OPT as PATHS
from utils import ensure_dir, save_csv

METRICS_FILE = os.path.join(PATHS["metrics"], "metrics.csv")

def evaluate_forecast(y_true: pd.Series, y_pred: pd.Series) -> dict:
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    mape = float(np.mean(np.abs((y_true - y_pred) / (y_true + 1e-9))) * 100)
    return {"forecast_rmse": rmse, "forecast_mae": mae, "forecast_mape": mape}

def evaluate_classification(y_true: pd.Series, y_pred: pd.Series) -> dict:
    return {
        "churn_accuracy": float(accuracy_score(y_true, y_pred)),
        "churn_f1": float(f1_score(y_true, y_pred)),
        "churn_roc_auc": float(roc_auc_score(y_true, y_pred))
    }

def evaluate_recommendations(recs_df: pd.DataFrame, ground_truth_df: pd.DataFrame = None, k: int = 5) -> dict:
    # If no ground truth provided, return basic stats
    if ground_truth_df is None:
        coverage = float(len(recs_df["product_id"].unique()) / (recs_df["product_id"].nunique() + 1e-9))
        return {"rec_coverage": coverage}
    # Precision@K
    precision_list = []
    for pid in ground_truth_df["product_id"].unique():
        true_set = set(ground_truth_df.loc[ground_truth_df["product_id"] == pid, "recommended_product_id"])
        preds = recs_df.loc[recs_df["product_id"] == pid].head(k)["recommended_product_id"].tolist()
        if len(preds) == 0 or len(true_set) == 0:
            continue
        precision_list.append(len(set(preds) & true_set) / len(preds))
    precision_at_k = float(np.mean(precision_list)) if precision_list else 0.0
    return {"precision@k": precision_at_k}

def export_metrics(metrics: dict):
    ensure_dir(PATHS["metrics"])
    df = pd.DataFrame([metrics])
    save_csv(df, METRICS_FILE)

if __name__ == "__main__":
    # Example wiring: load produced outputs and compute metrics
    # Forecast metrics
    forecast_csv = os.path.join(PATHS["models"], "prophet_forecast.csv")
    if os.path.exists(forecast_csv):
        forecast_df = pd.read_csv(forecast_csv, parse_dates=["ds"])
        # compute using historical overlap
        phase1 = pd.read_csv(PATHS["phase1_clean"], parse_dates=["transaction_date"])
        y_true = phase1.groupby("transaction_date")["revenue"].sum().reset_index().rename(columns={"transaction_date":"ds"})
        merged = y_true.merge(forecast_df, on="ds", how="left").fillna(0)
        f_metrics = evaluate_forecast(merged["revenue"], merged["yhat"])
    else:
        f_metrics = {}

    # Churn metrics
    lr_preds_file = os.path.join(PATHS["models"], "lr_churn_predictions.csv")
    if os.path.exists(lr_preds_file):
        preds = pd.read_csv(lr_preds_file)["prediction"]
        y_true = pd.read_csv(PATHS["phase1_clean"])["churn_flag"]
        c_metrics = evaluate_classification(y_true.iloc[:len(preds)], preds)
    else:
        c_metrics = {}

    # Recs metrics (basic)
    recs_file = os.path.join(PATHS["models"], "recommendations.csv")
    if os.path.exists(recs_file):
        recs = pd.read_csv(recs_file)
        r_metrics = evaluate_recommendations(recs)
    else:
        r_metrics = {}

    metrics = {**f_metrics, **c_metrics, **r_metrics}
    export_metrics(metrics)
    print(f"Metrics exported -> {METRICS_FILE}")
