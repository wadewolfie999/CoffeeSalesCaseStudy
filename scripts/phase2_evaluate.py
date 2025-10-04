import pandas as pd
import os
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, accuracy_score, roc_auc_score, f1_score

from utils import ensure_dir, save_csv
from config import PATHS

# Forecasting evaluation
def evaluate_forecast(y_true, y_pred):
    y_true, y_pred = pd.Series(y_true), pd.Series(y_pred)
    rmse = root_mean_squared_error(y_true, y_pred, squared=False)
    mae = mean_absolute_error(y_true, y_pred)
    mape = (abs((y_true - y_pred) / y_true).replace([float("inf")], 0)).mean() * 100
    return {"RMSE": rmse, "MAE": mae, "MAPE": mape}

# Churn / classification evaluation
def evaluate_classification(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "roc_auc": roc_auc_score(y_true, y_pred),
        "f1_score": f1_score(y_true, y_pred)
    }

# Recommendation evaluation: Precision@K, Recall@K
def evaluate_recommendations(recs_df, ground_truth_df, k=5):
    """
    recs_df: columns = ['product_id', 'recommended_product_id']
    ground_truth_df: actual co-purchased items for evaluation
    """
    precision_list, recall_list = [], []

    for item in ground_truth_df["product_id"].unique():
        true_items = set(ground_truth_df.loc[ground_truth_df["product_id"] == item, "recommended_product_id"])
        pred_items = set(recs_df.loc[recs_df["product_id"] == item, "recommended_product_id"].head(k))
        if len(pred_items) == 0 or len(true_items) == 0:
            continue
        precision_list.append(len(pred_items & true_items) / len(pred_items))
        recall_list.append(len(pred_items & true_items) / len(true_items))

    precision = sum(precision_list) / len(precision_list) if precision_list else 0
    recall = sum(recall_list) / len(recall_list) if recall_list else 0
    return {"precision@k": precision, "recall@k": recall}

def export_metrics(metrics_dict, filename="metrics.csv"):
    ensure_dir(PATHS["metrics"])
    out_path = os.path.join(PATHS["metrics"], filename)
    df = pd.DataFrame([metrics_dict])
    save_csv(df, out_path)

if __name__ == "__main__":
    # Example: Forecast evaluation
    forecast_df = pd.read_csv(os.path.join(PATHS["models"], "forecast.csv"))
    y_true = pd.read_csv(PATHS["phase1_clean"])[["transaction_date","revenue"]].groupby("transaction_date").sum()["revenue"]
    y_pred = forecast_df.set_index("ds")["yhat"].reindex(y_true.index, fill_value=0)
    forecast_metrics = evaluate_forecast(y_true, y_pred)

    # Example: Churn evaluation
    churn_true = pd.read_csv(PATHS["phase1_clean"])["churn_flag"]
    churn_pred = pd.read_csv(os.path.join(PATHS["models"], "lr_churn_predictions.csv"))["churn_prediction"]
    churn_metrics = evaluate_classification(churn_true, churn_pred)

    # Example: Recommendations evaluation
    recs_df = pd.read_csv(os.path.join(PATHS["models"], "recommendations.csv"))
    # ground_truth_df can be created or sampled from transaction history for evaluation
    ground_truth_df = recs_df.copy()  # placeholder for demo
    rec_metrics = evaluate_recommendations(recs_df, ground_truth_df, k=5)

    # Combine all metrics
    all_metrics = {**forecast_metrics, **churn_metrics, **rec_metrics}
    export_metrics(all_metrics)
    print("Evaluation metrics computed and exported.")
