import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/customers_cleaned.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH)

# Recreate income quartiles using the same method as segment analysis
valid_income = df["Income"].notna()
income_ranks = df.loc[valid_income, "Income"].rank(method="first")

df["Income_Quartile"] = pd.NA
df.loc[valid_income, "Income_Quartile"] = pd.qcut(
    income_ranks,
    q=4,
    labels=["Q1 (Lowest)", "Q2", "Q3", "Q4 (Highest)"]
).astype(str)

df["Children_Group"] = (
    (df["Kidhome"] + df["Teenhome"])
    .eq(0)
    .map({True: "0 children", False: "1+ children"})
)

# Select only the two qualifying, mutually exclusive groups
target_segments = [
    ("Q4 (Highest)", "0 children"),
    ("Q2", "0 children"),
]

target_mask = pd.Series(False, index=df.index)

for income_group, children_group in target_segments:
    target_mask |= (
        df["Income_Quartile"].eq(income_group)
        & df["Children_Group"].eq(children_group)
    )

targeted = df.loc[target_mask].copy()

# Validate that segments are mutually exclusive and complete
assert len(targeted) == 437
assert targeted["ID"].is_unique

# Profit assumptions from dataset
cost_per_contact = int(df["Z_CostContact"].iloc[0])
revenue_per_conversion = int(df["Z_Revenue"].iloc[0])

assert df["Z_CostContact"].nunique() == 1
assert df["Z_Revenue"].nunique() == 1

# Everyone scenario
all_contacted = len(df)
all_conversions = int(df["Response"].sum())
all_cost = all_contacted * cost_per_contact
all_revenue = all_conversions * revenue_per_conversion
all_profit = all_revenue - all_cost

# Targeted scenario
target_contacted = len(targeted)
target_conversions = targeted["Response"].sum()
target_rate = target_conversions / target_contacted
target_cost = target_contacted * cost_per_contact
target_revenue = target_conversions * revenue_per_conversion
target_profit = target_revenue - target_cost

# Segment-level detail
segment_rows = []

for income_group, children_group in target_segments:
    group = df[
        df["Income_Quartile"].eq(income_group)
        & df["Children_Group"].eq(children_group)
    ]

    segment_rows.append({
        "income_quartile": income_group,
        "children_group": children_group,
        "customers_contacted": len(group),
        "historical_conversions": int(group["Response"].sum()),
        "conversion_rate_pct": round(
            group["Response"].mean() * 100, 2
        ),
        "expected_conversions": (
            len(group) * group["Response"].mean()
        ),
    })

segment_detail = pd.DataFrame(segment_rows)

# Compare scenarios
comparison = pd.DataFrame([
    {
        "scenario": "Contact Everyone",
        "customers_contacted": all_contacted,
        "expected_conversions": all_conversions,
        "conversion_rate_pct": round(
            all_conversions / all_contacted * 100, 2
        ),
        "contact_cost": all_cost,
        "conversion_revenue": all_revenue,
        "profit": all_profit,
    },
    {
        "scenario": "Targeted Segments Only",
        "customers_contacted": target_contacted,
        "expected_conversions": round(target_conversions, 2),
        "conversion_rate_pct": round(target_rate * 100, 2),
        "contact_cost": target_cost,
        "conversion_revenue": target_revenue,
        "profit": target_profit,
    },
])

comparison.to_csv(
    OUTPUT_DIR / "targeted_profit_comparison.csv",
    index=False
)

segment_detail.to_csv(
    OUTPUT_DIR / "targeted_segment_details.csv",
    index=False
)

print("\n--- TARGETED SEGMENT DETAILS ---")
print(segment_detail.to_string(index=False))

print("\n--- PROFIT COMPARISON ---")
print(comparison.to_string(index=False))

print("\n--- ADDITIONAL METRICS ---")
print("Break-even conversion rate:",
      round(cost_per_contact / revenue_per_conversion * 100, 2), "%")
print("Targeted conversion rate:", round(target_rate * 100, 2), "%")
print("Profit improvement:", target_profit - all_profit)
print("Customers not contacted:", all_contacted - target_contacted)

print("\n--- VALIDATION ---")
assert target_contacted == 437
assert all_contacted == 2240
assert all_profit == -3046
assert target_profit == 262
assert target_profit > all_profit

print("Profit calculations and targeting validations passed.")
