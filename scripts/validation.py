import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# === 1. Load Environment Variables ===
load_dotenv()

username = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
port = os.getenv("MYSQL_PORT")
database = os.getenv("MYSQL_DB")

# === 2. Connect to MySQL ===

engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")

df = pd.read_sql("SELECT * FROM sales", engine)


# === 4. Basic Info ===
print("\n--- Data Info ---")
print(df.info())

print("\n--- Data Preview ---")
print(df.head())

# === 5. Missing Values ===
print("\n--- Missing Values ---")
print(df.isnull().sum())

# === 6. Descriptive Stats ===
print("\n--- Descriptive Statistics ---")
print(df.describe(include="all"))

# === 7. Duplicate Check ===
duplicates = df[df.duplicated(subset=["transaction_id"], keep=False)]
print(f"\nDuplicate Transactions: {len(duplicates)}")

# === 8. Outliers Check ===
outliers = df[(df["transaction_qty"] <= 0) | (df["unit_price"] <= 0)]
print(f"\nOutlier Rows: {len(outliers)}")
print(outliers.head())