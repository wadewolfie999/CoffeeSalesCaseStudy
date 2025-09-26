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

# === 2. Load Excel ===
excel_file = r"C:\Users\vahid\Projects\CoffeeSalesCaseStudy\data\Coffee-Shop-Sales.xlsx"
df = pd.read_excel(excel_file)

# === Clean Column Name ===
df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

# === Fixing Date and Time type before exporting this into MySQL ===
df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.date
df["transaction_time"] = pd.to_datetime(df["transaction_time"], format="%H:%M:%S").dt.time

# ---------------------------------
print("Connecting to MySQL...")
# === 3. Connect to MySQL ===

engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")

# === 4. Load data ===

df.to_sql("sales", engine, if_exists="replace", index=False, chunksize=1000)

print("DATA LOADED SUCCESSFULLY INTO MYSQL")