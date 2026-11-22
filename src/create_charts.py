import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT = Path("outputs/charts")
OUTPUT.mkdir(parents=True, exist_ok=True)

campaigns = pd.read_csv("outputs/campaign_confidence_intervals.csv")
spend = pd.read_csv("outputs/campaign_spend_comparison.csv")
segments = pd.read_csv("outputs/campaign6_segment_analysis.csv")

# Profit scenarios from the validated calculation
profit = pd.DataFrame({
    "scenario": ["Contact Everyone", "Targeted Segments Only"],
    "profit": [-3046, 262]
})

overall_rate = 334 / 2240 * 100

# -------------------------------------------------
# Chart 1: Campaign conversion rates and 95% CIs
# -------------------------------------------------

fig, ax = plt.subplots(figsize=(9, 5))

x = range(len(campaigns))
rates = campaigns["conversion_rate_pct"]

lower_error = rates - campaigns["ci_lower_pct"]
upper_error = campaigns["ci_upper_pct"] - rates

ax.errorbar(
    x,
    rates,
    yerr=[lower_error, upper_error],
    fmt="o",
    capsize=5
)

ax.set_xticks(list(x))
ax.set_xticklabels(campaigns["campaign"])
ax.set_ylabel("Conversion rate (%)")
ax.set_title(
    "Campaign 6 leads with a 14.91% conversion rate"
)
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()
fig.savefig(OUTPUT / "01_campaign_conversion_ci.png", dpi=300)
plt.close(fig)

# -------------------------------------------------
# Chart 2: Segment conversion rates
# -------------------------------------------------

selected_types = [
    "Income Quartile",
    "Education",
    "Marital Status",
    "Children at Home",
    "Customer Tenure"
]

plot_segments = segments[
    segments["segment_type"].isin(selected_types)
    & (segments["customers"] >= 50)
].copy()

plot_segments["label"] = (
    plot_segments["segment_type"]
    + ": "
    + plot_segments["segment"]
)

plot_segments = plot_segments.sort_values(
    "conversion_rate_pct"
)

fig, ax = plt.subplots(figsize=(11, 9))

ax.barh(
    plot_segments["label"],
    plot_segments["conversion_rate_pct"]
)

ax.axvline(
    overall_rate,
    linestyle="--",
    label=f"Overall: {overall_rate:.2f}%"
)

ax.set_xlabel("Campaign 6 conversion rate (%)")
ax.set_title(
    "Income, household size and tenure distinguish conversion performance"
)
ax.legend()
ax.grid(axis="x", alpha=0.3)

fig.tight_layout()
fig.savefig(OUTPUT / "02_segment_conversion_rates.png", dpi=300)
plt.close(fig)

# -------------------------------------------------
# Chart 3: Mean spending by conversion outcome
# -------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 5))

x = range(len(spend))
width = 0.36

ax.bar(
    [i - width / 2 for i in x],
    spend["mean_spend_converters"],
    width,
    label="Converters"
)

ax.bar(
    [i + width / 2 for i in x],
    spend["mean_spend_non_converters"],
    width,
    label="Non-converters"
)

ax.set_xticks(list(x))
ax.set_xticklabels(spend["campaign"])
ax.set_ylabel("Mean total product spend")
ax.set_title(
    "Campaign converters consistently spend more than non-converters"
)
ax.legend()
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()
fig.savefig(OUTPUT / "03_spend_by_conversion.png", dpi=300)
plt.close(fig)

# -------------------------------------------------
# Chart 4: Profit scenario comparison
# -------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    profit["scenario"],
    profit["profit"]
)

ax.axhline(0, linewidth=0.8)
ax.set_ylabel("Profit contribution")
ax.set_title(
    "Targeting selected segments changes estimated profit from loss to gain"
)
ax.grid(axis="y", alpha=0.3)

for bar, value in zip(bars, profit["profit"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value,
        f"{value:,.0f}",
        ha="center",
        va="bottom" if value >= 0 else "top"
    )

fig.tight_layout()
fig.savefig(OUTPUT / "04_profit_comparison.png", dpi=300)
plt.close(fig)

print("--- CHARTS CREATED ---")

for path in sorted(OUTPUT.glob("*.png")):
    print(path, "-", path.stat().st_size, "bytes")

assert len(list(OUTPUT.glob("*.png"))) == 4

print("\nAll four chart files created successfully.")
