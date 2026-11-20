import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import chi2_contingency

DATA_PATH = Path("data/processed/customers_cleaned.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH)
df["Dt_Customer"] = pd.to_datetime(df["Dt_Customer"])

# Total product spending across all six product categories
spend_columns = [
    "MntWines",
    "MntFruits",
    "MntMeatProducts",
    "MntFishProducts",
    "MntSweetProducts",
    "MntGoldProds",
]

df["Total_Spend"] = df[spend_columns].sum(axis=1)

# Age bands using latest registration year as reference
reference_year = df["Dt_Customer"].dt.year.max()

df["Age"] = reference_year - df["Year_Birth"]
df.loc[df["Year_Birth"] < 1920, "Age"] = np.nan

df["Age_Band"] = pd.cut(
    df["Age"],
    bins=[0, 29, 39, 49, 59, 120],
    labels=["18-29", "30-39", "40-49", "50-59", "60+"],
    include_lowest=True
)

# Income quartiles, excluding missing and anomalous income
valid_income = df["Income"].notna()
income_ranks = df.loc[valid_income, "Income"].rank(method="first")

df["Income_Quartile"] = pd.NA
df.loc[valid_income, "Income_Quartile"] = pd.qcut(
    income_ranks,
    q=4,
    labels=["Q1 (Lowest)", "Q2", "Q3", "Q4 (Highest)"]
).astype(str)

# Children at home
df["Children_Group"] = np.where(
    (df["Kidhome"] + df["Teenhome"]) == 0,
    "0 children",
    "1+ children"
)

# Customer tenure relative to latest registration date
reference_date = df["Dt_Customer"].max()
df["Tenure_Months"] = (
    (reference_date - df["Dt_Customer"]).dt.days / 30.4375
)

df["Tenure_Band"] = pd.cut(
    df["Tenure_Months"],
    bins=[-0.01, 6, 12, 18, 24, np.inf],
    labels=["0-6 months", "7-12 months", "13-18 months",
            "19-24 months", "24+ months"]
)

# Two-variable segment
df["Income_Children"] = (
    df["Income_Quartile"].astype("string")
    + " | "
    + df["Children_Group"]
)

# Segment definitions
# Day 8: Two-way segment analysis
segment_definitions = {
    "Income Quartile x Children": "Income_Children",
}

# Overall Campaign 6 conversion rate
overall_rate = df["Response"].mean()

results = []

for segment_type, column in segment_definitions.items():
    valid = df[df[column].notna()]

    for segment_value, group in valid.groupby(column, observed=True):
        n = len(group)
        conversions = int(group["Response"].sum())
        non_conversions = n - conversions
        rate = conversions / n

        # Compare this segment against all customers outside it
        others = valid[valid[column] != segment_value]

        table = [
            [conversions, non_conversions],
            [
                int(others["Response"].sum()),
                len(others) - int(others["Response"].sum())
            ]
        ]

        p_value = chi2_contingency(
            table,
            correction=False
        ).pvalue

        results.append({
            "segment_type": segment_type,
            "segment": str(segment_value),
            "customers": n,
            "conversions": conversions,
            "conversion_rate_pct": round(rate * 100, 2),
            "mean_total_spend": round(group["Total_Spend"].mean(), 2),
            "overall_rate_pct": round(overall_rate * 100, 2),
            "p_value": p_value,
            "high_performing": (
                n >= 50
                and rate > others["Response"].mean()
                and p_value < 0.05
            )
        })

results_df = pd.DataFrame(results)

results_df["p_value"] = results_df["p_value"].map(
    lambda value: round(value, 6)
)

results_df.to_csv(
    OUTPUT_DIR / "campaign6_two_way_segment_analysis.csv",
    index=False
)

print("\n--- ANALYSIS REFERENCE ---")
print("Reference year:", reference_year)
print("Reference date:", reference_date.date())
print("Overall Campaign 6 conversion rate:",
      round(overall_rate * 100, 2), "%")

print("\n--- SEGMENT PERFORMANCE ---")

for segment_type in segment_definitions:
    subset = results_df[
        results_df["segment_type"] == segment_type
    ].sort_values("conversion_rate_pct", ascending=False)

    print(f"\n{segment_type}")
    print(
        subset[
            [
                "segment",
                "customers",
                "conversions",
                "conversion_rate_pct",
                "mean_total_spend",
                "p_value",
                "high_performing"
            ]
        ].to_string(index=False)
    )

print("\n--- HIGH-PERFORMING SEGMENTS ---")

high_performers = results_df[
    results_df["high_performing"]
].sort_values("conversion_rate_pct", ascending=False)

if high_performers.empty:
    print("No segments met all three criteria.")
else:
    print(
        high_performers[
            [
                "segment_type",
                "segment",
                "customers",
                "conversion_rate_pct",
                "mean_total_spend",
                "p_value"
            ]
        ].to_string(index=False)
    )

print("\nSaved:", OUTPUT_DIR / "campaign6_two_way_segment_analysis.csv")

# Validation
assert results_df["customers"].gt(0).all()
assert results_df["conversion_rate_pct"].between(0, 100).all()
assert results_df["p_value"].between(0, 1).all()

print("\nSegment analysis validations passed.")
