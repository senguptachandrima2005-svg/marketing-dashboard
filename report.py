"""Module 5: Report generation (campaign report, marketing summary, monthly report)."""
import io
import pandas as pd
import kpi, insights

KPI_COLS = ["impressions", "clicks", "conversions", "spend", "revenue",
            "CTR_%", "Conv_Rate_%", "CPA", "ROI_%", "ROAS", "Engagement_Rate_%"]


def campaign_report(df) -> pd.DataFrame:
    return kpi.by_campaign(df).sort_values("ROI_%", ascending=False).round(2)


def channel_report(df) -> pd.DataFrame:
    return kpi.by_channel(df).sort_values("ROI_%", ascending=False).round(2)


def monthly_report(df) -> pd.DataFrame:
    m = kpi.trend(df, "MS")
    m["month"] = m["date"].dt.strftime("%Y-%m")
    m["Revenue_MoM_%"] = m["revenue"].pct_change() * 100
    return m[["month"] + KPI_COLS + ["Revenue_MoM_%"]].round(2)


def summary_text(df) -> str:
    lines = ["MARKETING PERFORMANCE SUMMARY",
             f"Period: {df['date'].min():%Y-%m-%d} to {df['date'].max():%Y-%m-%d}",
             f"Campaigns: {df['campaign_id'].nunique()} | Channels: {df['channel'].nunique()}", "",
             "KEY INSIGHTS"]
    lines += [f"- {i}" for i in insights.generate(df)]
    return "\n".join(lines)


def excel_bytes(df) -> bytes:
    """Workbook with campaign, channel, and monthly sheets (needs openpyxl; falls back to None)."""
    try:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as xw:
            campaign_report(df).to_excel(xw, "Campaigns", index=False)
            channel_report(df).to_excel(xw, "Channels", index=False)
            monthly_report(df).to_excel(xw, "Monthly", index=False)
        return buf.getvalue()
    except ImportError:
        return b""
