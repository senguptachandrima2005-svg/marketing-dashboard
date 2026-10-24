"""Module 2 (part 1): Data cleaning & preprocessing."""
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd

DB_PATH = Path("data/marketing.db")


def clean(df: pd.DataFrame):
    """Return (clean_df, log) where log documents each cleaning step."""
    log = {"rows_in": len(df)}
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    log["bad_dates_dropped"] = int(df["date"].isna().sum())
    df = df.dropna(subset=["date"])

    before = len(df)
    df = df.drop_duplicates()
    log["duplicates_removed"] = before - len(df)

    df["channel"] = df["channel"].str.strip().str.title()
    df["channel"] = df["channel"].replace({"Google Ads": "Google Ads", "Linkedin": "LinkedIn", "Youtube": "YouTube"})

    # negative values are invalid
    neg = df["spend"] < 0
    log["negative_spend_set_nan"] = int(neg.sum())
    df.loc[neg, "spend"] = np.nan

    # clicks cannot exceed impressions
    bad = df["clicks"] > df["impressions"]
    log["clicks_gt_impressions_set_nan"] = int(bad.sum())
    df.loc[bad, "clicks"] = np.nan

    # impute missing numeric values with the campaign median (fallback: channel median)
    for col in ["spend", "clicks"]:
        log[f"missing_{col}_imputed"] = int(df[col].isna().sum())
        df[col] = df[col].fillna(df.groupby("campaign_id")[col].transform("median"))
        df[col] = df[col].fillna(df.groupby("channel")[col].transform("median"))

    int_cols = ["impressions", "clicks", "conversions", "likes", "shares", "comments", "sessions"]
    df[int_cols] = df[int_cols].round().astype(int)
    df = df.sort_values(["date", "campaign_id"]).reset_index(drop=True)
    log["rows_out"] = len(df)
    return df, log


def main():
    with sqlite3.connect(DB_PATH) as con:
        raw = pd.read_sql("SELECT * FROM raw_campaigns", con)
        df, log = clean(raw)
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df.to_sql("campaigns", con, if_exists="replace", index=False)
    print("Cleaning log:")
    for k, v in log.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
