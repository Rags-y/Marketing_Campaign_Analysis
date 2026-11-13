import sqlite3
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/customers_cleaned.csv")
DB_PATH = Path("outputs/marketing_campaigns.sqlite")

df = pd.read_csv(DATA_PATH)

campaign_columns = {
    "Campaign 1": "AcceptedCmp1",
    "Campaign 2": "AcceptedCmp2",
    "Campaign 3": "AcceptedCmp3",
    "Campaign 4": "AcceptedCmp4",
    "Campaign 5": "AcceptedCmp5",
    "Campaign 6": "Response",
}

# -------------------------------
# Pandas campaign calculations
# -------------------------------

pandas_campaigns = []

for campaign, column in campaign_columns.items():
    conversions = int(df[column].sum())
    customers = len(df)
    rate = conversions / customers * 100

    pandas_campaigns.append({
        "campaign": campaign,
        "conversions": conversions,
        "customers_contacted": customers,
        "conversion_rate_pct": round(rate, 2)
    })

pandas_campaigns = pd.DataFrame(pandas_campaigns)

# -------------------------------
# Pandas Campaign 6 profit
# -------------------------------

cost_per_contact = int(df["Z_CostContact"].iloc[0])
revenue_per_conversion = int(df["Z_Revenue"].iloc[0])

assert df["Z_CostContact"].nunique() == 1
assert df["Z_Revenue"].nunique() == 1

customers_contacted = len(df)
conversions = int(df["Response"].sum())

total_contact_cost = customers_contacted * cost_per_contact
total_conversion_revenue = conversions * revenue_per_conversion
campaign_profit = total_conversion_revenue - total_contact_cost

# -------------------------------
# Read SQL results
# -------------------------------

with sqlite3.connect(DB_PATH) as conn:
    sql_campaigns = pd.read_sql_query(
        """
        SELECT 'Campaign 1' AS campaign,
               SUM(AcceptedCmp1) AS conversions,
               COUNT(*) AS customers_contacted,
               ROUND(100.0 * SUM(AcceptedCmp1) / COUNT(*), 2)
                   AS conversion_rate_pct
        FROM customers

        UNION ALL

        SELECT 'Campaign 2', SUM(AcceptedCmp2), COUNT(*),
               ROUND(100.0 * SUM(AcceptedCmp2) / COUNT(*), 2)
        FROM customers

        UNION ALL

        SELECT 'Campaign 3', SUM(AcceptedCmp3), COUNT(*),
               ROUND(100.0 * SUM(AcceptedCmp3) / COUNT(*), 2)
        FROM customers

        UNION ALL

        SELECT 'Campaign 4', SUM(AcceptedCmp4), COUNT(*),
               ROUND(100.0 * SUM(AcceptedCmp4) / COUNT(*), 2)
        FROM customers

        UNION ALL

        SELECT 'Campaign 5', SUM(AcceptedCmp5), COUNT(*),
               ROUND(100.0 * SUM(AcceptedCmp5) / COUNT(*), 2)
        FROM customers

        UNION ALL

        SELECT 'Campaign 6', SUM(Response), COUNT(*),
               ROUND(100.0 * SUM(Response) / COUNT(*), 2)
        FROM customers
        """,
        conn
    )

    sql_profit = pd.read_sql_query(
        """
        SELECT
            COUNT(*) AS customers_contacted,
            SUM(Response) AS conversions,
            COUNT(*) * MAX(Z_CostContact) AS total_contact_cost,
            SUM(Response) * MAX(Z_Revenue)
                AS total_conversion_revenue,
            SUM(Response) * MAX(Z_Revenue)
                - COUNT(*) * MAX(Z_CostContact) AS campaign_profit
        FROM customers
        """,
        conn
    ).iloc[0]

# -------------------------------
# Compare SQL and Pandas
# -------------------------------

sql_campaigns = (
    sql_campaigns
    .sort_values("campaign")
    .reset_index(drop=True)
)

pandas_campaigns = (
    pandas_campaigns
    .sort_values("campaign")
    .reset_index(drop=True)
)

pd.testing.assert_frame_equal(
    sql_campaigns,
    pandas_campaigns,
    check_dtype=False
)

assert customers_contacted == int(sql_profit["customers_contacted"])
assert conversions == int(sql_profit["conversions"])
assert total_contact_cost == int(sql_profit["total_contact_cost"])
assert total_conversion_revenue == int(
    sql_profit["total_conversion_revenue"]
)
assert campaign_profit == int(sql_profit["campaign_profit"])

# -------------------------------
# Display verification
# -------------------------------

print("\n--- PANDAS CAMPAIGN RESULTS ---")
print(pandas_campaigns.to_string(index=False))

print("\n--- PROFIT CROSS-CHECK ---")
print("Customers contacted:", customers_contacted)
print("Conversions:", conversions)
print("Contact cost:", total_contact_cost)
print("Conversion revenue:", total_conversion_revenue)
print("Campaign 6 profit:", campaign_profit)

print("\n--- VERIFICATION ---")
print("All six campaign conversion results match SQL.")
print("Campaign 6 profit matches SQL.")
print("All SQL-Pandas assertions passed.")
