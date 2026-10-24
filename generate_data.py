"""Module 1: Marketing data collection.
Generates a realistic self-created marketing dataset (allowed by the brief)
and loads it into SQLite. Deliberately includes dirty rows so Module 2 has
real cleaning work to do.
"""
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
DB_PATH = Path("data/marketing.db")
CSV_PATH = Path("data/marketing_raw.csv")

CHANNELS = {
    # channel: (cost per 1k impressions, base CTR, base conv rate, avg order value)
    "Google Ads":     (95.0, 0.045, 0.060, 85),
    "Facebook Ads":   (45.0, 0.022, 0.040, 60),
    "Instagram":      (55.0, 0.028, 0.035, 65),
    "Email":          (40.0, 0.060, 0.080, 75),
    "YouTube":        (60.0, 0.015, 0.035, 80),
    "LinkedIn":       (100.0, 0.012, 0.060, 150),
    "Organic Search": (25.0, 0.050, 0.050, 80),
}
CAMPAIGN_TYPES = ["Brand Awareness", "Lead Generation", "Seasonal Sale", "Retargeting", "Product Launch"]


def build_raw(n_days=180, seed=SEED):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2025-01-01", periods=n_days)
    rows, cid = [], 1
    for ch, (cpm, ctr, cvr, aov) in CHANNELS.items():
        for _ in range(8):  # 8 campaigns per channel
            ctype = rng.choice(CAMPAIGN_TYPES)
            length = int(rng.integers(20, 45))
            start = int(rng.integers(-length // 2, n_days - length // 2))
            start = max(start, 0)
            quality = rng.uniform(0.7, 1.4)  # campaign-level quality factor
            name = f"{ctype[:4].upper()}-{ch[:3].upper()}-{cid:03d}"
            for d in range(start, min(start + length, n_days)):
                impressions = int(rng.normal(25000, 6000) * quality)
                impressions = max(impressions, 1000)
                clicks = int(impressions * ctr * quality * rng.uniform(0.8, 1.2))
                conversions = int(clicks * cvr * quality * rng.uniform(0.7, 1.3))
                spend = round(impressions / 1000 * cpm * rng.uniform(0.9, 1.15), 2)
                revenue = round(conversions * aov * rng.uniform(0.85, 1.2), 2)
                likes = int(clicks * rng.uniform(0.3, 0.8))
                shares = int(likes * rng.uniform(0.05, 0.25))
                comments = int(likes * rng.uniform(0.03, 0.15))
                sessions = int(clicks * rng.uniform(0.85, 0.98))
                rows.append([cid, name, ch, ctype, dates[d].strftime("%Y-%m-%d"),
                             impressions, clicks, conversions, spend, revenue,
                             likes, shares, comments, sessions])
            cid += 1
    cols = ["campaign_id", "campaign_name", "channel", "campaign_type", "date",
            "impressions", "clicks", "conversions", "spend", "revenue",
            "likes", "shares", "comments", "sessions"]
    df = pd.DataFrame(rows, columns=cols)

    # --- inject data-quality problems for Module 2 ---
    n = len(df)
    df = pd.concat([df, df.sample(25, random_state=1)], ignore_index=True)       # duplicates
    df.loc[rng.choice(n, 30, replace=False), "spend"] = np.nan                   # missing spend
    df.loc[rng.choice(n, 20, replace=False), "clicks"] = np.nan                  # missing clicks
    idx = rng.choice(n, 15, replace=False)
    df.loc[idx, "channel"] = df.loc[idx, "channel"].str.lower()                  # inconsistent case
    df.loc[rng.choice(n, 10, replace=False), "clicks"] = df["impressions"] * 2   # clicks > impressions
    df.loc[rng.choice(n, 5, replace=False), "spend"] = -50                       # negative spend
    return df


def main():
    Path("data").mkdir(exist_ok=True)
    df = build_raw()
    df.to_csv(CSV_PATH, index=False)
    with sqlite3.connect(DB_PATH) as con:
        df.to_sql("raw_campaigns", con, if_exists="replace", index=False)
    print(f"Raw data: {len(df)} rows -> {CSV_PATH} and {DB_PATH}")


if __name__ == "__main__":
    main()
