# utils.py
import os
import pandas as pd
from sqlalchemy import create_engine
import logging
import config

def get_db_connection():
    """Create a SQLAlchemy engine for MySQL."""
    try:
        engine = create_engine(
            f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}"
            f"@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DB}"
        )
        logging.info("[OK] Database connection established.")
        return engine
    except Exception as e:
        logging.error(f"[FAIL] Database connection failed: {e}")
        raise

def safe_save_plot(fig, path: str):
    """Save a matplotlib/seaborn figure safely."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fig.savefig(path, bbox_inches="tight")
        logging.info(f"[OK] Plot saved: {path}")
    except Exception as e:
        logging.error(f"[FAIL] Could not save plot: {e}")

def save_dataframe(df: pd.DataFrame, csv_path: str, excel_path: str):
    """Save dataframe to Excel with summary statistics."""
    try:
        summary = df.describe(include="all").transpose()
        with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Cleaned Data", index=False)
            summary.to_excel(writer, sheet_name="Summary Stats")
        logging.info("[OK] Data exported successfully.")
    except Exception as e:
        logging.error(f"[FAIL] Could not save dataframe: {e}")

# === Phase 2 helpers ===
def ensure_dir(path):
    try:    
        os.makedirs(path, exist_ok=True)
        logging.info("[OK] Directories are ensured.--excel--")
    except Exception as e:
        logging.error(f"[FAIL] Error during directory check: {e}")
    
def save_csv(df: pd.DataFrame, path: str):
    try:
        ensure_dir(os.path.dirname(path))
        df.to_csv(path, index=False)
        logging.info("[OK] Data exported successfully.--csv--")
    except Exception as e:
        logging.error(f"Error during saving csv file: {e}")