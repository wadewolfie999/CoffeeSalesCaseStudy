import pandas as pd
import os
from prophet import Prophet
from utils import ensure_dir, save_csv
from config import PATHS

def prepare_forecast_df(df: pd.DataFrame, date_col="transaction_date", target_col="revenue") -> pd.DataFrame:
    """
    Prepare DataFrame for Prophet.
    """
    df = df[[date_col, target_col]].rename(columns={date_col: "ds", target_col: "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    return df.groupby("ds")["y"].sum().reset_index()

def train_prophet(df: pd.DataFrame) -> Prophet:
    """
    Train Prophet model on revenue data.
    """
    model = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=True)
    model.fit(df)
    return model

def forecast(model: Prophet, periods: int = 30) -> pd.DataFrame:
    """
    Forecast future revenue for given periods (days).
    """
    future = model.make_future_dataframe(periods=periods)
    forecast_df = model.predict(future)
    return forecast_df[["ds", "yhat", "yhat_lower", "yhat_upper"]]

def export_forecast(df: pd.DataFrame, filename: str = "forecast.csv"):
    ensure_dir(PATHS["models"])
    out_path = os.path.join(PATHS["models"], filename)
    save_csv(df, out_path)

if __name__ == "__main__":
    raw = pd.read_csv(PATHS["phase1_clean"])
    df_prophet = prepare_forecast_df(raw)
    model = train_prophet(df_prophet)
    forecast_df = forecast(model, periods=30)
    export_forecast(forecast_df)
    print("Forecast generated and exported.")
