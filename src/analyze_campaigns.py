import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = Path("data/processed/customers_cleaned.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH)

campaigns = {
    "Campaign 1": "AcceptedCmp1",
    "Campaign 2": "AcceptedCmp2",
    "Campaign 3": "AcceptedCmp3",
    "Campaign 4": "AcceptedCmp4",
    "Campaign 5": "AcceptedCmp5",
    "Campaign 6": "Response",
}

spend_columns = [
    "MntWines",
    "MntFruits",
    "MntMeatProducts",
    "MntFishProducts",
    "MntSweetProducts",
    "MntGoldProds",
]

df["Total_Spend"] = df[spend_columns].sum(axis=1)

# Wilson 95% confidence interval for a binomial proportion
def wilson_interval(successes, total, z=1.959963984540054):
    p = successes / total
    denominator = 1 + z**2 / total

    center = (
        p + z**2 / (2 * total)
    ) / denominator

    margin = (
        z * np.sqrt(
            p * (1 - p) / total
            + z**2 / (4 * total**2)
        )
    ) / denominator

    return center - margin, center + margin


campaign_results = []
spend_results = []

for campaign, column in campaigns.items():
    conversions = int(df[column].sum())
    total = len(df)
    rate = conversions / total

    lower, upper = wilson_interval(conversions, total)

    campaign_results.append({
        "campaign": campaign,
        "conversions": conversions,
        "customers": total,
        "conversion_rate_pct": round(rate * 100, 2),
        "ci_lower_pct": round(lower * 100, 2),
        "ci_upper_pct": round(upper * 100, 2),
    })

    converters = df.loc[df[column] == 1, "Total_Spend"]
    non_converters = df.loc[df[column] == 0, "Total_Spend"]

    spend_results.append({
        "campaign": campaign,
        "converter_count": len(converters),
        "mean_spend_converters": round(converters.mean(), 2),
        "non_converter_count": len(non_converters),
        "mean_spend_non_converters": round(
            non_converters.mean(), 2
        ),
        "spend_difference": round(
            converters.mean() - non_converters.mean(), 2
        ),
    })

campaign_df = pd.DataFrame(campaign_results)
spend_df = pd.DataFrame(spend_results)

campaign_df.to_csv(
    OUTPUT_DIR / "campaign_confidence_intervals.csv",
    index=False
)

spend_df.to_csv(
    OUTPUT_DIR / "campaign_spend_comparison.csv",
    index=False
)

# Campaign ranking
ranking = campaign_df.sort_values(
    "conversion_rate_pct",
    ascending=False
).reset_index(drop=True)

ranking.insert(0, "rank", range(1, len(ranking) + 1))

print("\n--- CAMPAIGN RANKING AND 95% WILSON CONFIDENCE INTERVALS ---")
print(ranking.to_string(index=False))

print("\n--- MEAN TOTAL SPEND: CONVERTERS VS NON-CONVERTERS ---")
print(spend_df.to_string(index=False))

print("\n--- SAVED FILES ---")
print("outputs/campaign_confidence_intervals.csv")
print("outputs/campaign_spend_comparison.csv")

assert len(campaign_df) == 6
assert campaign_df["ci_lower_pct"].le(
    campaign_df["conversion_rate_pct"]
).all()
assert campaign_df["ci_upper_pct"].ge(
    campaign_df["conversion_rate_pct"]
).all()

print("\nCampaign analysis validations passed.")
