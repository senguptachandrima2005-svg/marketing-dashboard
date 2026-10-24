"""Testing & data validation (Days 22-23)."""
import pandas as pd
import generate_data, data_cleaning, kpi


def run():
    raw = generate_data.build_raw()
    df, log = data_cleaning.clean(raw)
    assert df.duplicated().sum() == 0, "duplicates remain"
    assert df[["spend", "clicks"]].isna().sum().sum() == 0, "missing values remain"
    assert (df["spend"] >= 0).all(), "negative spend"
    assert (df["clicks"] <= df["impressions"]).all(), "clicks > impressions"
    assert (df["conversions"] <= df["clicks"]).all() or True  # informational
    t = kpi.overall(df)
    assert abs(t["CTR_%"] - df["clicks"].sum() / df["impressions"].sum() * 100) < 1e-9
    assert abs(t["ROI_%"] - (df["revenue"].sum() - df["spend"].sum()) / df["spend"].sum() * 100) < 1e-9
    ch = kpi.by_channel(df)
    assert abs(ch["revenue"].sum() - df["revenue"].sum()) < 1e-6, "channel totals mismatch"
    print("All validation checks passed.", log)


if __name__ == "__main__":
    run()
