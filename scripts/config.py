import os
import logging
from dotenv import load_dotenv

# === Base Paths ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# === Phase 1 output paths ===
PHASE1_DIR = os.path.join(OUTPUT_DIR, "phase1")
PHASE1_CLEAN = os.path.join(PHASE1_DIR, "clean")
PHASE1_PLOTS = os.path.join(PHASE1_DIR, "plots")
PHASE1_LOGS = os.path.join(PHASE1_DIR, "logs")


# === Phase 2 output paths ===
PHASE2_DIR = os.path.join(OUTPUT_DIR, "phase2")
PHASE2_FEATURES = os.path.join(PHASE2_DIR, "features")
PHASE2_MODELS = os.path.join(PHASE2_DIR, "models")
PHASE2_METRICS = os.path.join(PHASE2_DIR, "")
PHASE2_LOGS = os.path.join(PHASE2_DIR, "")

# === Phase 2 optimized paths ===
PHASE2_OPT_DIR = os.path.join(OUTPUT_DIR, "phase2_optimized")
PHASE2_OPT_FEATURES = os.path.join(PHASE2_OPT_DIR, "features")
PHASE2_OPT_MODELS = os.path.join(PHASE2_OPT_DIR, "models")
PHASE2_OPT_METRICS = os.path.join(PHASE2_OPT_DIR, "metrics")
PHASE2_OPT_LOGS = os.path.join(PHASE2_OPT_DIR, "logs")

# === Create all directories if not exist ===
for path in [PHASE1_CLEAN, PHASE1_PLOTS, PHASE1_LOGS,
             PHASE2_FEATURES, PHASE2_MODELS, PHASE2_METRICS, PHASE2_LOGS,
             PHASE2_OPT_FEATURES, PHASE2_OPT_MODELS, PHASE2_OPT_METRICS, PHASE2_OPT_LOGS]:
    os.makedir(path)


# === PATHS dictionary for Phase 2 scripts ===
PATHS = {
    "features": os.path.join(PHASE2_FEATURES, "features.csv"),
    "models": PHASE2_MODELS,
    "metrics": PHASE2_METRICS,
    "logs": PHASE2_LOGS,
    "phase1_clean": os.path.join(PHASE1_CLEAN, "clean_sales.csv")
}

# === PATHS dictionary for Phase 2.5 modules ===
PATHS_OPT = {
    "features": PHASE2_OPT_FEATURES,
    "models": PHASE2_OPT_MODELS,
    "metrics": PHASE2_OPT_METRICS,
    "logs": PHASE2_OPT_LOGS,
    "phase1_clean": PHASE1_CLEAN + "/clean_sales.csv"
}

# === Logging ===
LOG_FILE = os.path.join(PHASE1_LOGS, "pipeling.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# === Environment variables for DB access ===
load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")

