# Marketing Performance Dashboard

Data analytics capstone: track, analyze and visualize marketing campaign performance across channels.

## Quick start
```bash
pip install -r requirements.txt
python generate_data.py     # Module 1: build dataset + SQLite DB
python data_cleaning.py     # Module 2: clean -> `campaigns` table
python tests.py             # Testing & data validation
streamlit run app.py        # Module 3: dashboard (auto-builds the DB if missing)
```

## Structure
| File | Module | Purpose |
|---|---|---|
| generate_data.py | 1 | Self-created marketing dataset (7 channels, 56 campaigns, ~6 months) with injected data-quality issues; loads SQLite |
| data_cleaning.py | 2 | Dedupe, standardise channel names, fix invalid values, impute missing values, log every step |
| kpi.py | 2 | CTR, conversion rate, CPC, CPA, ROI, ROAS, engagement rate by channel/campaign/type/time |
| app.py | 3 | Streamlit dashboard: Overview, Channels, Campaigns, Insights, Reports tabs with filters |
| insights.py | 4 | Rule-based insights: best campaigns, high-conversion channels, trends, recommendations |
| report.py | 5 | Campaign report, marketing summary, monthly report (CSV / TXT / XLSX downloads) |
| tests.py | - | Validation checks on cleaning and KPI maths |

## KPI definitions
- CTR = clicks / impressions
- Conversion rate = conversions / clicks
- CPC = spend / clicks; CPA = spend / conversions
- ROI = (revenue - spend) / spend; ROAS = revenue / spend
- Engagement rate = (likes + shares + comments) / impressions

## Using real data
Replace `data/marketing_raw.csv` / the `raw_campaigns` table with a Kaggle or Google Analytics export that has the same columns, then run `data_cleaning.py`.

## Deploy (Streamlit Cloud)
Push to GitHub -> share.streamlit.io -> New app -> select repo, main file `app.py`. The app builds its own database on first launch.

## Scope
Per the brief: no real-time systems, ML prediction, CRM integrations or cloud pipelines.
