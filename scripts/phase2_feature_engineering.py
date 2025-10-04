import pandas as pd
import numpy as np
import os
from config import PATHS
from utils import ensure_dir, save_csv

def compute_revenue_growth(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    agg = (
        df.groupby(pd.Grouper(key="transaction_date", freq=freq))["revenue"]
        .sum()
        .reset_index()
    )
    agg["revenue_growth"] = agg["revenue"].pct_change().fillna(0)
    agg.rename(columns={"transaction_date": "period"}, inplace=True)
    return agg

def compute_category_mix(df: pd.DataFrame) -> pd.DataFrame:
    total_rev = df.groupby("store_id")["revenue"].sum().reset_index(name="total_revenue")
    cat_rev = (
        df.groupby(["store_id", "category"])["revenue"]
        .sum()
        .reset_index(name="cat_revenue")
    )
    merged = pd.merge(cat_rev, total_rev, on="store_id")
    merged["category_mix_pct"] = merged["cat_revenue"] / merged["total_revenue"]
    return merged

def build_feature_matrix(df: pd.DataFrame, features: list = None) -> pd.DataFrame:
    feature_dfs = []

    if features is None or "growth" in features:
        feature_dfs.append(compute_revenue_growth(df))

    if features is None or "category_mix" in features:
        feature_dfs.append(compute_category_mix(df))

    if len(feature_dfs) > 1:
        feat_matrix = pd.concat(feature_dfs, axis=1)
    else:
        feat_matrix = feature_dfs[0]

    return feat_matrix

def export_features(df: pd.DataFrame, filename: str = "features.csv"):
    ensure_dir(PATHS["features"])
    out_path = os.path.join(PATHS["features"], filename)
    save_csv(df, out_path)

if __name__ == "__main__":
    raw = pd.read_csv(PATHS["phase1_clean"])
    feats = build_feature_matrix(raw, features=["growth", "category_mix"])
    export_features(feats)
