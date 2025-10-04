import os
import pandas as pd
import numpy as np
from config import PATHS_OPT as PATHS
from utils import ensure_dir, save_csv

FEATURES_FILE = os.path.join(PATHS["features"], "features.csv")

def compute_revenue_growth(df: pd.DataFrame, group_col: str = "store_location", freq: int = 7) -> pd.DataFrame:
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df = df.sort_values(["transaction_date"])
    df["rev_lag"] = df.groupby(group_col)["revenue"].shift(1)
    df["revenue_growth"] = (df["revenue"] - df["rev_lag"]) / df["rev_lag"].replace(0, np.nan)
    df["revenue_growth"] = df["revenue_growth"].fillna(0)
    return df

def compute_category_mix(df: pd.DataFrame) -> pd.DataFrame:
    cat = df.groupby([ "store_location", "product_category"])["revenue"].sum().reset_index()
    total = df.groupby("store_location")["revenue"].sum().reset_index(name="total_revenue")
    merged = cat.merge(total, on="store_location", how="left")
    merged["category_mix_pct"] = merged["revenue"] / merged["total_revenue"].replace(0, np.nan)
    merged["category_mix_pct"] = merged["category_mix_pct"].fillna(0)
    # pivot so each category becomes a column per store
    pivot = merged.pivot_table(index="store_location", columns="product_category", values="category_mix_pct", fill_value=0)
    pivot = pivot.reset_index()
    pivot.columns.name = None
    return pivot

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["dow"] = df["transaction_date"].dt.dayofweek
    df["month"] = df["transaction_date"].dt.month
    df["day"] = df["transaction_date"].dt.day
    df["is_weekend"] = df["dow"].isin([5,6]).astype(int)
    return df

def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    # transaction-level time features + growth
    df_tf = add_time_features(df)
    df_growth = compute_revenue_growth(df_tf)
    # store-level category mix pivot
    cat_mix = compute_category_mix(df)
    # merge: left join transaction rows with store-level category mix
    feat = df_growth.merge(cat_mix, how="left", on="store_location")
    # example rolling metric per store
    feat["rev_7d_mean"] = feat.groupby("store_location")["revenue"].transform(lambda x: x.rolling(7, min_periods=1).mean())
    # drop helpers
    feat = feat.drop(columns=["rev_lag"], errors="ignore")
    return feat

def export_features(df: pd.DataFrame, path: str = FEATURES_FILE):
    ensure_dir(os.path.dirname(path))
    save_csv(df, path)

if __name__ == "__main__":
    raw_path = PATHS["phase1_clean"]
    raw = pd.read_csv(raw_path, parse_dates=["transaction_date"])
    feats = build_feature_matrix(raw)
    export_features(feats)
    print.info(f"Features exported -> {FEATURES_FILE}")
