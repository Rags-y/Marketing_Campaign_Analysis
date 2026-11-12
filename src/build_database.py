import sqlite3
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/customers_cleaned.csv")
DB_PATH = Path("outputs/marketing_campaigns.sqlite")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

with sqlite3.connect(DB_PATH) as conn:
    df.to_sql(
        "customers",
        conn,
        if_exists="replace",
        index=False
    )

    row_count = conn.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    unique_ids = conn.execute(
        "SELECT COUNT(DISTINCT ID) FROM customers"
    ).fetchone()[0]

print("--- DATABASE CREATED ---")
print("Database:", DB_PATH)
print("Rows:", row_count)
print("Unique customer IDs:", unique_ids)

assert row_count == 2240
assert unique_ids == 2240

print("Database validation passed.")
