# run_hyperparameter_tuning.py
from scripts.phase2_optimized_hyperparameter_tuning import (
    tune_logistic_regression,
    tune_random_forest,
    tune_prophet,
    tune_arima
)

if __name__ == "__main__":
    # Example: Churn dataset
    dataset_path = "data/processed/churn_data.csv"
    target_column = "churned"

    # Logistic Regression
    best_lr = tune_logistic_regression(dataset_path, target_column)
    print("Best Logistic Regression Params:", best_lr)

    # Random Forest
    best_rf = tune_random_forest(dataset_path, target_column)
    print("Best Random Forest Params:", best_rf)

    # Forecasting dataset
    forecast_path = "data/processed/sales_forecast.csv"

    # Prophet
    best_prophet = tune_prophet(forecast_path)
    print("Best Prophet Params:", best_prophet)

    # ARIMA
    best_arima = tune_arima(forecast_path)
    print("Best ARIMA Params:", best_arima)
