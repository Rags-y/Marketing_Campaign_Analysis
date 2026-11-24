# Marketing Campaign Analysis

End-to-end analysis of the iFood marketing campaign dataset using Python, Pandas, SQLite, statistical analysis, and visualization.

## Objective
Compare six campaign response rates, identify customer segments associated with stronger Campaign 6 conversion, and estimate broad versus targeted outreach contribution.

## Dataset
- 2,240 customers, 29 original columns.
- One row per customer.
- Six campaign response indicators.
- Source: `data/raw/ml_project1_data.csv`.

## Key Findings
- Campaign 6: 334 conversions; 14.91% conversion rate (95% Wilson CI: 13.50%?16.45%).
- Campaign 2: lowest conversion rate at 1.34%.
- 239 customers (10.67%) accepted more than one campaign.
- Highest income quartile: 26.90% Campaign 6 conversion.
- Zero children at home: 26.49% conversion.
- Selected target group: 437 customers; 32.72% historical conversion rate.

## Estimated Contribution
Assumptions: contact cost = 3 units; conversion revenue = 11 units; break-even conversion rate = 27.27%.

| Scenario | Contacted | Conversions | Rate | Contribution |
|---|---:|---:|---:|---:|
| Contact everyone | 2,240 | 334 | 14.91% | -3,046 |
| Selected target group | 437 | 143 expected | 32.72% | +262 |

The target group combines mutually exclusive segments:
- Highest income quartile, zero children: 386 customers.
- Second income quartile, zero children: 51 customers.

These are in-sample estimates, not guaranteed future results. Prospective randomized validation is recommended.

## Data Cleaning
- Retained missing income values without imputation.
- Excluded one extreme income value (666,666) from analytical calculations while preserving the original.
- Excluded three implausible birth years from age-band calculations.
- Grouped Alone, Absurd, and YOLO marital-status labels as `Other/Unusual`.
- Recorded cleaning actions, reasons, and affected rows in `logs/cleaning_log.csv`.
- Used 2014 as the age reference year, based on the latest customer date.

## Statistical Methodology
- Campaign confidence intervals use the 95% Wilson method.
- Segment comparisons use chi-square tests against customers outside each segment.
- High-performing segments require at least 50 customers, a higher conversion rate than the complement, and p < 0.05.
- Income quartiles exclude missing and anomalous analytical income values.
- SQL and Pandas campaign conversion and Campaign 6 contribution calculations are independently checked using assertions.
- Segment p-values are exploratory and unadjusted for multiple comparisons. CI overlap is not a formal pairwise significance test.

## Project Structure
- `data/raw/`: original dataset
- `data/processed/`: cleaned dataset
- `notebooks/`: reproducible Jupyter notebook
- `src/`: analysis and reporting scripts
- `sql/queries.sql`: SQL queries
- `logs/`: cleaning log
- `outputs/`: database, analysis outputs, and charts
- `reports/marketing_campaign_analysis.pdf`: final report

## Requirements
Python 3.10+; pandas, numpy, matplotlib, seaborn, scipy, jupyter, nbformat, reportlab, and pypdf.

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install pandas numpy matplotlib seaborn scipy jupyter nbformat reportlab pypdf
Run the Analysis
```

## Run from the project root:
python .\src\clean_data.py
python .\src\build_database.py
python .\src\verify_sql_pandas.py
python .\src\analyze_segments.py
python .\src\analyze_campaigns.py
python .\src\calculate_profit.py
python .\src\create_charts.py
python .\src\create_report.py


Execute the notebook:
jupyter nbconvert --to notebook --execute --inplace .\notebooks\marketing_campaign_analysis.ipynb


## Deliverables
- Jupyter notebook
- SQLite database and SQL queries
- Cleaned dataset and cleaning log
- Campaign and segment analysis outputs
- Four charts
- PDF report (maximum five pages)

## Limitations
- Historical response does not establish causation.
- Target selection and evaluation use the same historical outcomes, creating potential selection bias.
- Segment tests are exploratory and unadjusted for multiple comparisons.
- Contribution excludes costs and revenue not represented by the dataset constants.
- Randomized prospective validation is recommended before deployment.

## Author
Raghav Kumar
