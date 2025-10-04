import os
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from config import PATHS_OPT as PATHS
from utils import ensure_dir, save_csv

MODEL_DIR = PATHS["models"]
RECS_FILE = os.path.join(MODEL_DIR, "recommendations.csv")

def build_item_matrix(df: pd.DataFrame):
    # transaction_id × product_id binary matrix
    trans_prod = pd.crosstab(df["transaction_id"], df["product_id"])
    prod_ids = trans_prod.columns.tolist()
    matrix = csr_matrix(trans_prod.values)
    return matrix, prod_ids, trans_prod

def build_item_similarity(matrix: csr_matrix):
    # cosine similarity on item vectors (columns)
    # compute item vectors by transposing transaction-product matrix
    item_mat = matrix.T
    sim = cosine_similarity(item_mat)
    return sim

def recommend_topk(sim_matrix: np.ndarray, prod_ids: list, top_k: int = 10):
    recs = []
    idx_map = {i: pid for i, pid in enumerate(prod_ids)}
    for i in range(sim_matrix.shape[0]):
        row = sim_matrix[i]
        # ignore self similarity
        row[i] = -np.inf
        top_idx = np.argsort(row)[-top_k:][::-1]
        for j in top_idx:
            recs.append((idx_map[i], idx_map[j], float(row[j])))
    recs_df = pd.DataFrame(recs, columns=["product_id", "recommended_product_id", "score"])
    return recs_df

def export_recommendations(recs_df: pd.DataFrame):
    ensure_dir(MODEL_DIR)
    save_csv(recs_df, RECS_FILE)

if __name__ == "__main__":
    raw = pd.read_csv(PATHS["phase1_clean"])
    matrix, prod_ids, pivot = build_item_matrix(raw)
    sim = build_item_similarity(matrix)
    recs = recommend_topk(sim, prod_ids, top_k=5)
    export_recommendations(recs)
    print(f"Recommendations saved -> {RECS_FILE}")
