import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging
import config
from utils import get_db_connection, safe_save_plot, save_dataframe

# === 1. Load Data ===
def load_data():
    logging.info("[START] Loading data from MySQL...")
    engine = get_db_connection()
    df = pd.read_sql("SELECT * FROM sales", con=engine)
    logging.info(f"[OK] Data loaded: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df

# === 2. Clean & Transform ===
def clean_transform(df: pd.DataFrame) -> pd.DataFrame:
    logging.info("[START] Cleaning & transforming data...")
    df.columns = [c.lower().strip() for c in df.columns]

    if "transaction_id" in df.columns:
        before = len(df)
        df = df.dropna(subset=["transaction_id"])
        logging.info(f"[OK] Dropped {before - len(df)} rows with missing transaction_id.")

    if "transaction_date" in df.columns:
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
        df["year"] = df["transaction_date"].dt.year
        df["month"] = df["transaction_date"].dt.month
        df["day"] = df["transaction_date"].dt.day
        df["dow"] = df["transaction_date"].dt.dayofweek

    if {"transaction_qty", "unit_price"}.issubset(df.columns):
        df["revenue"] = df["transaction_qty"] * df["unit_price"]
        logging.info("[OK] Revenue column created.")

    logging.info("[OK] Cleaning done.")
    return df

# === 3. EDA Plots ===
def plot_eda(df: pd.DataFrame):
    logging.info("[START] Generating plots...")

    if "transaction_date" in df.columns and "revenue" in df.columns:
        fig, ax = plt.subplots(figsize=(10,5))
        df.groupby("transaction_date")["revenue"].sum().plot(ax=ax)
        ax.set(title="Total Sales Over Time", ylabel="Revenue")
        safe_save_plot(fig, f"{config.PHASE1_PLOTS}/sales_over_time.png")
        plt.close(fig)

    if "product_category" in df.columns:
        fig, ax = plt.subplots(figsize=(10,5))
        df.groupby("product_category")["revenue"].sum().nlargest(5).plot(kind="bar", ax=ax)
        ax.set(title="Top 5 Products by Revenue", ylabel="Revenue")
        safe_save_plot(fig, f"{config.PHASE1_PLOTS}/top_products.png")
        plt.close(fig)

    if "store_location" in df.columns:
        fig, ax = plt.subplots(figsize=(10,5))
        df.groupby("store_location")["revenue"].sum().plot(kind="bar", ax=ax)
        ax.set(title="Revenue by Store", ylabel="Revenue")
        safe_save_plot(fig, f"{config.PHASE1_PLOTS}/revenue_by_store.png")
        plt.close(fig)

    if {"year", "month", "revenue"}.issubset(df.columns):
        fig, ax = plt.subplots(figsize=(8,5))
        monthly = df.groupby(["year", "month"])["revenue"].sum().reset_index()
        monthly["year_month"] = pd.to_datetime(monthly["year"].astype(str) + "-" + monthly["month"].astype(str) + "-01")
        sns.lineplot(x="year_month", y="revenue", data=monthly, markers="o", ax=ax)
        ax.set(title="Monthly Revenue Trend", xlabel="Month", ylabel="Revenue")
        safe_save_plot(fig, f"{config.PHASE1_PLOTS}/monthly_revenue_trend.png")
        plt.close(fig)

    if {"store_location", "product_category"}.issubset(df.columns):
        fig, ax = plt.subplots(figsize=(12,6))
        pivot = df.pivot_table(values="revenue", index="store_location", columns="product_category", aggfunc="sum", fill_value=0)
        sns.heatmap(pivot, cmap="YlGnBu", ax=ax)
        ax.set(title="Revenue by Store and Product Category", ylabel="Store", xlabel="Category")
        plt.tight_layout()
        safe_save_plot(fig, f"{config.PHASE1_PLOTS}/store_product_heatmap.png")
        plt.close(fig)

    logging.info("[OK] Plots generated.")

# === 4. Export Results ===
def export_results(df: pd.DataFrame):
    logging.info("[START] Exporting results...")
    save_dataframe(
        df,
        csv_path=f"{config.PHASE1_CLEAN}/clean_sales.csv",
        excel_path=f"{config.PHASE1_CLEAN}/clean_sales.xlsx"
    )

# === 5. Main ===
def run_pipeline():
    logging.info("[START] Phase 1 Data Pipeline...")
    try:
        df = load_data()
        df = clean_transform(df)
        plot_eda(df)
        export_results(df)
        logging.info("[OK] Phase 1 completed successfully.")
    except Exception as e:
        logging.critical(f"[FAIL] Pipeline failed: {e}")

if __name__ == "__main__":
    run_pipeline()
