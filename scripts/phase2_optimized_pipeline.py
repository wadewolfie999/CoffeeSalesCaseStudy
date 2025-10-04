import os
import pandas as pd

from config import PATHS_OPT as PATHS
from phase2_optimized_feature_engineering import build_feature_matrix, export_features, build_feature_matrix as gen_features
from phase2_optimized_models_churn import (train_logistic_regression, train_random_forest,
                                           tune_random_forest, predict, export_predictions, log_shap)
from phase2_optimized_forecasting import prepare_forecast_df, train_prophet, forecast, rolling_cv_prophet
from phase2_optimized_recommender import build_item_matrix, build_item_similarity, recommend_topk, export_recommendations
from phase2_optimized_evaluate import evaluate_forecast, evaluate_classification, evaluate_recommendations, export_metrics

def run_phase2_optimized(horizon: int = 30, tune_rf: bool = True):
    raw = pd.read_csv(PATHS["phase1_clean"], parse_dates=["transaction_date"])
    # features
    from phase2_optimized_feature_engineering import build_feature_matrix as build_feats
    feats = build_feats(raw)
    export_features(feats)

    # prepare X, y for churn
    drop_cols = ["transaction_id", "product_id", "product_category", "transaction_date", "store_location"]
    X = feats.drop(columns=[c for c in drop_cols if c in feats.columns], errors="ignore").fillna(0)
    y_full = pd.read_csv(PATHS["phase1_clean"])["churn_flag"]
    y = y_full.iloc[:len(X)].reset_index(drop=True)

    # train churn models
    lr = train_logistic_regression(X, y)
    if tune_rf:
        rf = tune_random_forest(X, y)
    else:
        rf = train_random_forest(X, y)

    lr_preds = predict(lr, X)
    rf_preds = predict(rf, X)
    export_predictions(lr_preds, "lr_churn_predictions.csv")
    export_predictions(rf_preds, "rf_churn_predictions.csv")

    try:
        log_shap(rf, X)
    except Exception:
        pass

    # forecasting
    ts = prepare_forecast_df(raw)
    prophet_model = train_prophet(ts)
    forecast_df = forecast(prophet_model, periods=horizon)

    # rolling cv (optional)
    try:
        _ = rolling_cv_prophet(ts, n_splits=3)
    except Exception:
        pass

    # recommender
    matrix, prod_ids, _ = build_item_matrix(raw)
    sim = build_item_similarity(matrix)
    recs = recommend_topk(sim, prod_ids, top_k=5)
    from phase2_optimized_recommender import export_recommendations as exp_rec
    exp_rec(recs)

    # evaluation
    # forecast eval: align historical overlap
    y_true = raw.groupby("transaction_date")["revenue"].sum().reset_index().rename(columns={"transaction_date":"ds"})
    merged = y_true.merge(forecast_df, on="ds", how="left").fillna(0)
    f_metrics = evaluate_forecast(merged["revenue"], merged["yhat"])
    c_metrics = evaluate_classification(y, lr_preds)
    r_metrics = evaluate_recommendations(recs)
    all_metrics = {**f_metrics, **c_metrics, **r_metrics}
    export_metrics(all_metrics)

    print("Phase2 optimized run complete. Outputs in:", PATHS["models"], PATHS["features"], PATHS["metrics"])

if __name__ == "__main__":
    run_phase2_optimized(horizon=30, tune_rf=True)
