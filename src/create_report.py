from pathlib import Path
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "marketing_campaign_analysis.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

campaigns = pd.read_csv(ROOT / "outputs/campaign_confidence_intervals.csv")
spend = pd.read_csv(ROOT / "outputs/campaign_spend_comparison.csv")
segments = pd.read_csv(ROOT / "outputs/campaign6_segment_analysis.csv")
cleaning = pd.read_csv(ROOT / "logs/cleaning_log.csv")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="ReportTitle", parent=styles["Title"],
    fontSize=20, leading=24, alignment=TA_CENTER,
    textColor=colors.HexColor("#17365D"), spaceAfter=8
))
styles.add(ParagraphStyle(
    name="Section", parent=styles["Heading2"],
    fontSize=13, leading=16, textColor=colors.HexColor("#17365D"),
    spaceBefore=5, spaceAfter=6
))
styles.add(ParagraphStyle(
    name="BodySmall", parent=styles["BodyText"],
    fontSize=8.5, leading=11, spaceAfter=5
))
styles.add(ParagraphStyle(
    name="Small", parent=styles["BodyText"],
    fontSize=7.2, leading=9
))
styles.add(ParagraphStyle(
    name="SubTitle", parent=styles["Heading3"],
    fontSize=10, leading=12, textColor=colors.HexColor("#24476B"),
    spaceBefore=4, spaceAfter=4
))

def money(value):
    return f"{value:,.2f}"

def make_table(data, widths, font_size=7.5):
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 2),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D2DC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F1F5F9")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table

def chart(path, height=145):
    img = Image(str(ROOT / path), width=515, height=height, kind="proportional")
    img.hAlign = "CENTER"
    return img

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(18 * mm, 12 * mm, "Marketing Campaign Analysis | iFood customer dataset")
    canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(
    str(OUT), pagesize=A4,
    rightMargin=17 * mm, leftMargin=17 * mm,
    topMargin=15 * mm, bottomMargin=20 * mm,
    title="Marketing Campaign Analysis",
    author="Marketing Campaign Analysis"
)

story = []

# -------------------------------------------------------------------
# PAGE 1 — EXECUTIVE SUMMARY AND DATA QUALITY
# -------------------------------------------------------------------
story.append(Paragraph("Marketing Campaign Analysis", styles["ReportTitle"]))
story.append(Paragraph(
    "iFood customer dataset | 2,240 customers | Six campaign response indicators",
    styles["BodySmall"]
))
story.append(Paragraph("Executive summary", styles["Section"]))
story.append(Paragraph(
    "Campaign 6 recorded the strongest response: 334 customers converted "
    "(14.91%; 95% Wilson CI: 13.50%–16.45%). However, under the dataset's "
    "contact-cost and conversion-revenue assumptions, contacting every "
    "customer produces a negative estimated contribution of 3,046 units. "
    "A narrowly selected, historical high-response group produces a "
    "positive in-sample estimate, but requires prospective validation.",
    styles["BodySmall"]
))

story.append(Paragraph("Three numerical recommendations", styles["Section"]))
recommendations = [
    "<b>1. Use Campaign 6 as the response benchmark.</b> It generated "
    "334 conversions from 2,240 customers (14.91%), more than any other "
    "campaign in the dataset.",
    "<b>2. Avoid assuming broad outreach is profitable.</b> The estimated "
    "break-even response rate is 27.27% (3 contact-cost units / 11 "
    "conversion-revenue units); the overall Campaign 6 rate was 14.91%.",
    "<b>3. Pilot a targeted group before scaling.</b> The selected "
    "437-customer group had a historical 32.72% response rate and an "
    "estimated contribution of +262 units, versus -3,046 units for "
    "contacting everyone. Validate with a randomized holdout."
]
for item in recommendations:
    story.append(Paragraph(item, styles["BodySmall"]))

story.append(Paragraph("Data preparation and cleaning", styles["Section"]))
story.append(Paragraph(
    "The raw dataset contains 2,240 customer records and 29 original "
    "columns. No duplicate rows or duplicate customer IDs were found. "
    "The cleaning pipeline preserved original fields and logged each "
    "intervention. Missing income values were retained as missing rather "
    "than imputed. One extreme income value (666,666) was excluded from "
    "income-based analysis while preserving the original value. Three "
    "implausible birth years (before 1920) were excluded from age-band "
    "calculations. Seven rare marital-status records (Alone, Absurd, "
    "YOLO) were grouped as Other/Unusual.",
    styles["BodySmall"]
))

clean_rows = [["Data issue", "Rows", "Treatment"]]
for _, row in cleaning.iterrows():
    action = str(row["action"])
    if len(action) > 75:
        action = action[:72] + "..."
    clean_rows.append([
        str(row["issue"]),
        str(int(row["rows_affected"])),
        Paragraph(action, styles["Small"])
    ])
story.append(make_table(clean_rows, [105, 38, 350], 7))
story.append(Spacer(1, 5))
story.append(Paragraph(
    "<b>Additional campaign metric:</b> 239 customers (10.67%) accepted "
    "more than one of the six campaigns; the maximum was five.",
    styles["BodySmall"]
))

story.append(PageBreak())

# -------------------------------------------------------------------
# PAGE 2 — CAMPAIGN COMPARISON
# -------------------------------------------------------------------
story.append(Paragraph("Campaign performance", styles["Section"]))
campaigns = campaigns.copy()
campaigns["rank"] = campaigns["conversion_rate_pct"].rank(
    ascending=False, method="min"
).astype(int)
campaigns = campaigns.sort_values("rank")

campaign_rows = [[
    "Rank", "Campaign", "Conversions", "Rate", "95% Wilson CI"
]]
for _, row in campaigns.iterrows():
    campaign_rows.append([
        str(int(row["rank"])),
        str(row["campaign"]),
        str(int(row["conversions"])),
        f'{row["conversion_rate_pct"]:.2f}%',
        f'{row["ci_lower_pct"]:.2f}%–{row["ci_upper_pct"]:.2f}%'
    ])
story.append(make_table(
    campaign_rows, [38, 85, 85, 70, 215], 7.5
))
story.append(Spacer(1, 5))
story.append(chart("outputs/charts/01_campaign_conversion_ci.png", 155))
story.append(Paragraph(
    "Campaign 6's confidence interval does not overlap the intervals "
    "for the other five campaigns. Campaigns 3 and 5 have identical "
    "observed rates and intervals; Campaign 4's interval overlaps those "
    "of Campaigns 3 and 5. Interval overlap is descriptive and is not a "
    "substitute for formal pairwise hypothesis testing.",
    styles["BodySmall"]
))

story.append(Paragraph("Customer spending by campaign response", styles["Section"]))
story.append(chart("outputs/charts/03_spend_by_conversion.png", 145))
story.append(Paragraph(
    "For every campaign, customers who accepted it had higher mean total "
    "spend than customers who did not. This is an association in the "
    "observed dataset; it does not establish that campaign contact caused "
    "higher spending.",
    styles["BodySmall"]
))

story.append(PageBreak())

# -------------------------------------------------------------------
# PAGE 3 — SEGMENT ANALYSIS
# -------------------------------------------------------------------
story.append(Paragraph("Campaign 6 customer segments", styles["Section"]))
story.append(Paragraph(
    "Segments were assessed using size, Campaign 6 conversion rate, "
    "mean total spend, and a chi-square comparison against customers "
    "outside each segment. A segment is labelled high-performing only "
    "when it has at least 50 customers and a significantly higher rate "
    "(p < 0.05).",
    styles["BodySmall"]
))
story.append(chart("outputs/charts/02_segment_conversion_rates.png", 205))

qualified = segments[
    (segments["high_performing"].astype(str).str.lower() == "true")
].copy().sort_values("conversion_rate_pct", ascending=False)

segment_rows = [[
    "Segment", "Customers", "Conversions", "Rate", "Mean spend", "p-value"
]]
for _, row in qualified.iterrows():
    segment_rows.append([
        Paragraph(f'{row["segment_type"]}: {row["segment"]}', styles["Small"]),
        str(int(row["customers"])),
        str(int(row["conversions"])),
        f'{row["conversion_rate_pct"]:.2f}%',
        money(row["mean_total_spend"]),
        f'{row["p_value"]:.4f}'
    ])
story.append(make_table(
    segment_rows, [145, 58, 60, 60, 85, 85], 7
))
story.append(Spacer(1, 5))
story.append(Paragraph(
    "The strongest one-dimensional results include the highest income "
    "quartile (26.90%), customers with no children at home (26.49%), "
    "19–24-month tenure (26.75%), and PhD education (20.78%). Single, "
    "divorced, and widow marital-status groups also met the exploratory "
    "threshold. These definitions overlap: their customer counts must "
    "not be added together.",
    styles["BodySmall"]
))
story.append(Paragraph(
    "The two-variable analysis identified the highest-income/no-children "
    "group (386 customers; 33.68%) and the second-income-quartile/no-children "
    "group (51 customers; 25.49%). The latter only narrowly meets the "
    "minimum sample-size threshold.",
    styles["BodySmall"]
))

story.append(PageBreak())

# -------------------------------------------------------------------
# PAGE 4 — PROFIT, TARGETING, LIMITATIONS
# -------------------------------------------------------------------
story.append(Paragraph("Targeting and estimated contribution", styles["Section"]))
story.append(Paragraph(
    "The profit calculation uses the dataset constants Z_CostContact = 3 "
    "per contacted customer and Z_Revenue = 11 per campaign conversion. "
    "It is a simplified contribution estimate, not full accounting profit "
    "or customer product-spend revenue.",
    styles["BodySmall"]
))

profit_rows = [
    ["Measure", "Contact everyone", "Selected target group"],
    ["Customers contacted", "2,240", "437"],
    ["Historical / expected conversions", "334", "143"],
    ["Conversion rate", "14.91%", "32.72%"],
    ["Contact cost", "6,720", "1,311"],
    ["Conversion revenue", "3,674", "1,573"],
    ["Estimated contribution", "-3,046", "+262"],
]
story.append(make_table(profit_rows, [190, 150, 150], 8))
story.append(Spacer(1, 6))
story.append(chart("outputs/charts/04_profit_comparison.png", 165))
story.append(Paragraph(
    "The targeted group consists of two mutually exclusive combinations: "
    "highest income quartile with zero children at home (n=386; 130 "
    "historical conversions) and second income quartile with zero children "
    "at home (n=51; 13 historical conversions). Together, they represent "
    "437 distinct customers. The estimate assumes each group's observed "
    "Campaign 6 conversion rate repeats. It reduces contact volume by "
    "1,803 customers and improves estimated contribution by 3,308 units.",
    styles["BodySmall"]
))

story.append(Paragraph("Limitations and interpretation", styles["Section"]))
limitations = [
    "The targeting estimate is in-sample: segments were selected and "
    "evaluated using the same historical Campaign 6 outcomes. It is likely "
    "optimistic and is not a forecast guarantee.",
    "Segment p-values are exploratory and unadjusted for multiple "
    "comparisons. Small groups, especially the 51-customer segment, "
    "need additional validation.",
    "Confidence-interval overlap is not a formal pairwise significance "
    "test. No causal effect of campaign contact can be inferred from "
    "these observational comparisons.",
    "The profit proxy uses only the supplied contact cost and conversion "
    "revenue constants. It excludes other operating costs, margin "
    "differences, and long-term customer value.",
    "Age uses 2014 as the reference year, based on the latest customer "
    "date in the dataset. Income-based analyses exclude missing and "
    "anomalous income values."
]
for item in limitations:
    story.append(Paragraph("• " + item, styles["BodySmall"]))

story.append(Paragraph(
    "<b>Next step:</b> Run a prospective randomized test comparing the "
    "selected target group with a suitable control group, then evaluate "
    "realized incremental conversions and contribution before scaling.",
    styles["BodySmall"]
))

doc.build(story, onFirstPage=footer, onLaterPages=footer)

print("PDF report created:", OUT)
print("File size:", OUT.stat().st_size, "bytes")
