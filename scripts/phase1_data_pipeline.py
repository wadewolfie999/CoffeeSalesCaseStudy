"""
RUN FROM PROJECT ROOT
Phase 1 Pipeline for Coffee Sales Case Study
- Load data from MySQL database
- Clean and transform data
- Generate EDA plots
- Export cleaned dataset & summary plots
- Save logs to outputs/logs
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging

# === Setup paths ===
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","outputs"))
CLEAN_DIR = os.path.join(OUTPUT_DIR, "clean")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")
LOG_DIR = os.path.join(OUTPUT_DIR, "logs")

for d in [CLEAN_DIR, PLOTS_DIR, LOG_DIR]:
    os.makedirs(d, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

# === Setup logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# === 1. Load Data ===
def load_data():
    logging.info("[START] Loading data from MySQL database...")
    load_dotenv()
    username = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST")
    port = os.getenv("MYSQL_PORT")
    database = os.getenv("MYSQL_DB")

    try:
        engine = create_engine(
            f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        )
        df = pd.read_sql("SELECT * FROM sales", con=engine)
        logging.info(f"[OK] Data loaded: {df.shape[0]} rows, {df.shape[1]} columns.")
        return df
    except Exception as e:
        logging.error(f"[FAIL] Failed to load data: {e}")
        raise

# === 2. Clean & Transform ===
def clean_transform(df: pd.DataFrame) -> pd.DataFrame:
    logging.info("[START] Cleaning and transforming data...")

    df.columns = [c.lower().strip() for c in df.columns]

    if "transaction_id" in df.columns:
        before = len(df)
        df = df.dropna(subset=["transaction_id"])
        after = len(df)
        logging.info(f"[OK] Dropped {before - after} rows with missing transaction_id.")

    if "transaction_date" in df.columns:
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
        df["year"] = df["transaction_date"].dt.year
        df["month"] = df["transaction_date"].dt.month
        df["day"] = df["transaction_date"].dt.day
        df["dow"] = df["transaction_date"].dt.dayofweek

    if "transaction_qty" in df.columns and "unit_price" in df.columns:
        df["revenue"] = df["transaction_qty"] * df["unit_price"]
        logging.info("[OK] Revenue column created.")

    logging.info("[OK] Data cleaning and transformation done.")
    return df

# === 3. EDA Plots ===
def plot_eda(df: pd.DataFrame, save_dir=PLOTS_DIR):
    logging.info("[START] Generating and saving EDA plots...")
    os.makedirs(save_dir, exist_ok=True)

    try:
        if "transaction_date" in df.columns and "revenue" in df.columns:
            plt.figure(figsize=(10,5))
            df.groupby("transaction_date")["revenue"].sum().plot()
            plt.title("Total Sales Over Time")
            plt.ylabel("Revenue")
            plt.savefig(f"{save_dir}/sales_over_time.png")
            plt.close()
            logging.info("[OK] Plot saved: sales_over_time.png")

        if "product_category" in df.columns:
            plt.figure(figsize=(10,5))
            df.groupby("product_category")["revenue"].sum().nlargest(5).plot(kind="bar")
            plt.title("Top 5 Products by Revenue")
            plt.ylabel("Revenue")
            plt.savefig(f"{save_dir}/top_products.png")
            plt.close()
            logging.info("[OK] Plot saved: top_products.png")

        if "store_location" in df.columns:
            plt.figure(figsize=(10,5))
            df.groupby("store_location")["revenue"].sum().plot(kind="bar")
            plt.title("Revenue by Store")
            plt.ylabel("Revenue")
            plt.savefig(f"{save_dir}/revenue_by_store.png")
            plt.close()
            logging.info("[OK] Plot saved: revenue_by_store.png")
        
        if "year" in df.columns and "month" in df.columns and "revenue" in df.columns:
            plt.figure(figsize=(8,5))
            monthly = df.groupby(["year", "month"])["revenue"].sum().reset_index()
            monthly["year_month"] = pd.to_datetime(monthly["year"].astype(str) + "-" + monthly["month"].astype(str) + "-01")
            sns.lineplot(x="year_month", y="revenue", data=monthly, markers="o")
            plt.title("Monthly Revenue Trend")
            plt.ylabel("Revenue")
            plt.xlabel("Month")
            plt.savefig(f"{save_dir}/monthly_revenue_trend.png")
            plt.close()
            logging.info("[OK] Plot saved: monthly_revenue_trend.png")

        if "store_location" in df.columns and "product_category" in df.columns:
            plt.figure(figsize=(12,6))
            pivot = df.pivot_table(
                values="revenue", index="store_location", columns="product_category",
                aggfunc="sum", fill_value=0
                )
            sns.heatmap(pivot, cmap="YlGnBu")
            plt.title("Revenue by Store and Product Category")
            plt.ylabel("Store Location")
            plt.xlabel("Product Category")
            plt.tight_layout()
            plt.savefig(f"{save_dir}/store_product_heatmap.png")
            plt.close()
            logging.info("[OK] Plot saved: store_product_heatmap.png")

    except Exception as e:
        logging.error(f"[FAIL] Error during plotting: {e}")
        
# === 4. Export Results ===
def export_results(df: pd.DataFrame, data_dir=CLEAN_DIR):
    logging.info("[START] Exporting cleaned dataset and summary statistics...")
    os.makedirs(data_dir, exist_ok=True)

    try:
        # --- CSV ---
        df.to_csv(f"{data_dir}/clean_sales.csv", index=False)
        logging.info("[OK] CSV file saved: clean_sales.csv")

        # --- Excel with two sheets ---
        summary = df.describe(include="all").transpose()
        excel_path = f"{data_dir}/clean_sales.xlsx"
        with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Cleaned Data", index=False)
            summary.to_excel(writer, sheet_name="Summary Stats")
        logging.info("[OK] Excel file saved: clean_sales.xlsx")

    except Exception as e:
        logging.error(f"[FAIL] Failed to export data: {e}")

# === 5. Main Pipeline ===
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

if __name__=='__main__':
    run_pipeline()
