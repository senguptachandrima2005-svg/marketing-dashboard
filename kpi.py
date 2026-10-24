"""Module 2 (part 2): KPI analysis. Pure functions on a cleaned DataFrame."""
import numpy as np
import pandas as pd


def _safe_div(a, b):
    return np.where(b == 0, 0, a / np.where(b == 0, 1, b))


def add_kpis(g: pd.DataFrame) -> pd.DataFrame:
    """Given a grouped-sum frame, add the standard marketing KPIs."""
    g = g.copy()
    g["CTR_%"] = _safe_div(g["clicks"], g["impressions"]) * 100
    g["Conv_Rate_%"] = _safe_div(g["conversions"], g["clicks"]) * 100
    g["CPC"] = _safe_div(g["spend"], g["clicks"])
    g["CPA"] = _safe_div(g["spend"], g["conversions"])
    g["ROI_%"] = _safe_div(g["revenue"] - g["spend"], g["spend"]) * 100
    g["ROAS"] = _safe_div(g["revenue"], g["spend"])
    eng = g["likes"] + g["shares"] + g["comments"]
    g["Engagement_Rate_%"] = _safe_div(eng, g["impressions"]) * 100
    return g


SUM_COLS = ["impressions", "clicks", "conversions", "spend", "revenue",
            "likes", "shares", "comments", "sessions"]


def overall(df: pd.DataFrame) -> pd.Series:
    return add_kpis(df[SUM_COLS].sum().to_frame().T).iloc[0]


def by_channel(df):
    return add_kpis(df.groupby("channel")[SUM_COLS].sum()).reset_index()


def by_campaign(df):
    g = df.groupby(["campaign_id", "campaign_name", "channel", "campaign_type"])[SUM_COLS].sum()
    return add_kpis(g).reset_index()


def by_type(df):
    return add_kpis(df.groupby("campaign_type")[SUM_COLS].sum()).reset_index()


def trend(df, freq="W"):
    t = df.set_index("date")[SUM_COLS].resample(freq).sum()
    return add_kpis(t).reset_index()
