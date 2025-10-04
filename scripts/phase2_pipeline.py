import pandas as pd
from phase2_feature_engineering import generate_features
from phase2_models_churn import train_logistic_regression, train_random_forest, predict, export_predictions
from phase2_forecasting import prepare_forecast_df, train_prophet, forecast, export_forecast
from phase2_recommender import build_cooccurrence_matrix, recommend_items, export_recommendations
from phase2_evaluate import evaluate_forecast, evaluate_classification, evaluate_recommendations, export_metrics
from config import PATHS

def run_phase2_pipeline():
    # Load raw cleaned data from Phase 1
    raw_df = pd.read_csv(PATHS["phase1_clean"])

    # === 1. Feature Engineering ===
    features_df = generate_features(raw_df)
    features_df.to_csv(PATHS["features"], index=False)

    # === 2. Churn Prediction ===
    y_churn = raw_df["churn_flag"]
    lr_model = train_logistic_regression(features_df, y_churn)
    rf_model = train_random_forest(features_df, y_churn)

    lr_preds = predict(lr_model, features_df)
    rf_preds = predict(rf_model, features_df)

    export_predictions(lr_preds, "lr_churn_predictions.csv")
    export_predictions(rf_preds, "rf_churn_predictions.csv")

    # === 3. Forecasting ===
    forecast_df = prepare_forecast_df(raw_df)
    prophet_model = train_prophet(forecast_df)
    forecast_res = forecast(prophet_model, periods=30)
    export_forecast(forecast_res)

    # === 4. Recommendations ===
    cooc_matrix = build_cooccurrence_matrix(raw_df)
    recs_df = recommend_items(cooc_matrix, top_n=5)
    export_recommendations(recs_df)

    # === 5. Evaluation ===
    # Forecast metrics
    y_true_forecast = raw_df.groupby("transaction_date")["revenue"].sum()
    y_pred_forecast = forecast_res.set_index("ds")["yhat"].reindex(y_true_forecast.index, fill_value=0)
    forecast_metrics = evaluate_forecast(y_true_forecast, y_pred_forecast)

    # Churn metrics
    churn_metrics = evaluate_classification(y_churn, lr_preds)

    # Recommendation metrics
    # Placeholder: using predicted recommendations as ground truth for demo
    rec_metrics = evaluate_recommendations(recs_df, recs_df, k=5)

    # Combine all metrics and export
    all_metrics = {**forecast_metrics, **churn_metrics, **rec_metrics}
    export_metrics(all_metrics)

    print("Phase 2 pipeline completed successfully.")

if __name__ == "__main__":
    run_phase2_pipeline()
