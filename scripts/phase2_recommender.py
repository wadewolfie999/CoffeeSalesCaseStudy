import pandas as pd
import numpy as np
import os
from config import PATHS
from utils import ensure_dir, save_csv

def build_cooccurrence_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build item-item co-occurrence matrix from transactions.
    """
    # Create binary transaction × product matrix
    trans_prod = pd.crosstab(df["transaction_id"], df["product_id"])
    # Compute item-item similarity via co-occurrence
    cooc = trans_prod.T.dot(trans_prod)
    np.fill_diagonal(cooc.values, 0)  # Remove self-count
    return cooc

def recommend_items(cooc_matrix: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Generate top-N recommendations per product.
    """
    recommendations = {}
    for item in cooc_matrix.index:
        top_items = cooc_matrix.loc[item].nlargest(top_n).index.tolist()
        recommendations[item] = top_items
    rec_df = pd.DataFrame(
        [(k, v) for k, lst in recommendations.items() for v in lst],
        columns=["product_id", "recommended_product_id"]
    )
    return rec_df

def export_recommendations(rec_df: pd.DataFrame, filename: str = "recommendations.csv"):
    ensure_dir(PATHS["models"])
    out_path = os.path.join(PATHS["models"], filename)
    save_csv(rec_df, out_path)

if __name__ == "__main__":
    df = pd.read_csv(PATHS["phase1_clean"])
    cooc = build_cooccurrence_matrix(df)
    recs = recommend_items(cooc, top_n=5)
    export_recommendations(recs)
    print("Item-based recommendations generated and exported.")
