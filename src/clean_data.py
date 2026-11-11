import pandas as pd
from pathlib import Path

# Project paths
RAW_PATH = Path("data/raw/ml_project1_data.csv")
PROCESSED_DIR = Path("data/processed")
LOG_DIR = Path("logs")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Load original dataset
df = pd.read_csv(RAW_PATH)

# Preserve original values in the working dataframe
clean = df.copy()
clean["Income_Original"] = clean["Income"]
clean["Year_Birth_Original"] = clean["Year_Birth"]
clean["Marital_Status_Original"] = clean["Marital_Status"]

cleaning_log = []

def log_action(issue, action, reason, affected_rows, affected_ids):
    cleaning_log.append({
        "issue": issue,
        "action": action,
        "reason": reason,
        "rows_affected": affected_rows,
        "customer_ids": ", ".join(map(str, affected_ids))
    })

# 1. Missing income
missing_income = clean["Income"].isna()
log_action(
    "Missing Income",
    "Retained as NaN; no imputation",
    "Avoid inventing customer income; exclude only from income-dependent analyses",
    int(missing_income.sum()),
    clean.loc[missing_income, "ID"].tolist()
)

# 2. Extreme income
extreme_income = clean["Income"] > 200000
extreme_ids = clean.loc[extreme_income, "ID"].tolist()

clean.loc[extreme_income, "Income"] = pd.NA

log_action(
    "Extreme Income",
    "Set analytical Income to NaN; original value preserved",
    "Income of 666666 is an extreme anomaly and could distort quartiles and averages",
    int(extreme_income.sum()),
    extreme_ids
)

# 3. Implausible birth years
implausible_birth = clean["Year_Birth"] < 1920

log_action(
    "Implausible Birth Year",
    "Preserved original year; excluded from age-band calculations",
    "Avoid assigning implausible ages while retaining the original customer record",
    int(implausible_birth.sum()),
    clean.loc[implausible_birth, "ID"].tolist()
)

# 4. Marital status grouping for analysis
unusual_statuses = ["Alone", "Absurd", "YOLO"]

unusual_status = clean["Marital_Status"].isin(unusual_statuses)

clean["Marital_Status_Clean"] = clean["Marital_Status"].where(
    ~unusual_status,
    "Other/Unusual"
)

log_action(
    "Rare Marital Status",
    "Grouped Alone, Absurd and YOLO as Other/Unusual in analytical column",
    "Avoid unsupported recoding; preserve original labels in source column",
    int(unusual_status.sum()),
    clean.loc[unusual_status, "ID"].tolist()
)

# 5. Age calculation using latest customer registration year
latest_customer_year = pd.to_datetime(
    clean["Dt_Customer"]
).dt.year.max()

clean["Age"] = latest_customer_year - clean["Year_Birth"]

clean.loc[implausible_birth, "Age"] = pd.NA

# Save cleaned dataset and audit log
clean.to_csv(
    PROCESSED_DIR / "customers_cleaned.csv",
    index=False
)

pd.DataFrame(cleaning_log).to_csv(
    LOG_DIR / "cleaning_log.csv",
    index=False
)

# Validation summary
print("\n--- CLEANING SUMMARY ---")
print("Original rows:", len(df))
print("Cleaned rows:", len(clean))
print("Latest customer year:", latest_customer_year)
print("Missing analytical income:", clean["Income"].isna().sum())
print("Missing age:", clean["Age"].isna().sum())
print("Unique cleaned marital statuses:")
print(clean["Marital_Status_Clean"].value_counts().to_string())

print("\n--- SAVED FILES ---")
print(PROCESSED_DIR / "customers_cleaned.csv")
print(LOG_DIR / "cleaning_log.csv")

print("\n--- FINAL VALIDATION ---")
assert len(clean) == len(df)
assert clean["ID"].is_unique
assert clean.loc[extreme_income, "Income"].isna().all()
assert clean.loc[implausible_birth, "Age"].isna().all()
assert clean["Marital_Status_Clean"].notna().all()

print("All cleaning validations passed.")
