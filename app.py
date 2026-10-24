"""Module 3: Streamlit dashboard.  Run:  streamlit run app.py"""
import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

import kpi, insights, report
import generate_data, data_cleaning

st.set_page_config(page_title="Marketing Performance Dashboard", page_icon="📈", layout="wide")


@st.cache_data
def load() -> pd.DataFrame:
    # Build the database on first run (handy for Streamlit Cloud deployment)
    if not Path(generate_data.DB_PATH).exists():
        generate_data.main()
        data_cleaning.main()
    with sqlite3.connect(generate_data.DB_PATH) as con:
        try:
            df = pd.read_sql("SELECT * FROM campaigns", con, parse_dates=["date"])
        except Exception:
            data_cleaning.main()
            df = pd.read_sql("SELECT * FROM campaigns", con, parse_dates=["date"])
    return df


df_all = load()

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")
dmin, dmax = df_all["date"].min().date(), df_all["date"].max().date()
dr = st.sidebar.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
channels = st.sidebar.multiselect("Channels", sorted(df_all["channel"].unique()),
                                  default=sorted(df_all["channel"].unique()))
types = st.sidebar.multiselect("Campaign types", sorted(df_all["campaign_type"].unique()),
                               default=sorted(df_all["campaign_type"].unique()))

start, end = (dr if isinstance(dr, tuple) and len(dr) == 2 else (dmin, dmax))
df = df_all[(df_all["date"].dt.date >= start) & (df_all["date"].dt.date <= end)
            & df_all["channel"].isin(channels) & df_all["campaign_type"].isin(types)]

st.title("📈 Marketing Performance Dashboard")
if df.empty:
    st.warning("No data for the selected filters.")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Channels", "Campaigns", "Insights", "Reports"])

# ---------------- Overview ----------------
with tab1:
    t = kpi.overall(df)
    c = st.columns(6)
    c[0].metric("Spend", f"${t['spend']:,.0f}")
    c[1].metric("Revenue", f"${t['revenue']:,.0f}")
    c[2].metric("ROI", f"{t['ROI_%']:.0f}%")
    c[3].metric("CTR", f"{t['CTR_%']:.2f}%")
    c[4].metric("Conv. rate", f"{t['Conv_Rate_%']:.2f}%")
    c[5].metric("CPA", f"${t['CPA']:.2f}")
    c = st.columns(4)
    c[0].metric("Impressions (reach)", f"{t['impressions']:,.0f}")
    c[1].metric("Clicks", f"{t['clicks']:,.0f}")
    c[2].metric("Conversions", f"{t['conversions']:,.0f}")
    c[3].metric("ROAS", f"{t['ROAS']:.2f}x")

    freq = st.radio("Trend granularity", ["Daily", "Weekly", "Monthly"], index=1, horizontal=True)
    tr = kpi.trend(df, {"Daily": "D", "Weekly": "W", "Monthly": "MS"}[freq])
    l, r = st.columns(2)
    l.plotly_chart(px.line(tr, x="date", y=["spend", "revenue"], title="Spend vs Revenue"),
                   use_container_width=True)
    r.plotly_chart(px.line(tr, x="date", y="Engagement_Rate_%", title="Engagement rate trend (%)"),
                   use_container_width=True)
    st.plotly_chart(px.line(tr, x="date", y=["CTR_%", "Conv_Rate_%"], title="CTR and conversion rate (%)"),
                    use_container_width=True)

# ---------------- Channels ----------------
with tab2:
    ch = kpi.by_channel(df)
    l, r = st.columns(2)
    l.plotly_chart(px.bar(ch.sort_values("ROI_%"), x="ROI_%", y="channel", orientation="h",
                          title="ROI by channel (%)", color="ROI_%"), use_container_width=True)
    r.plotly_chart(px.bar(ch, x="channel", y="Conv_Rate_%", title="Conversion rate by channel (%)",
                          color="channel"), use_container_width=True)
    l, r = st.columns(2)
    l.plotly_chart(px.pie(ch, names="channel", values="spend", title="Spend share"),
                   use_container_width=True)
    r.plotly_chart(px.scatter(ch, x="CPA", y="ROI_%", size="revenue", color="channel",
                              title="Cost per acquisition vs ROI (bubble = revenue)"),
                   use_container_width=True)
    st.dataframe(ch.round(2), use_container_width=True)

# ---------------- Campaigns ----------------
with tab3:
    cp = kpi.by_campaign(df)
    metric = st.selectbox("Rank campaigns by", ["ROI_%", "revenue", "Conv_Rate_%", "CTR_%", "ROAS"])
    n = st.slider("Show top N", 5, 25, 10)
    top = cp.sort_values(metric, ascending=False).head(n)
    st.plotly_chart(px.bar(top, x=metric, y="campaign_name", orientation="h", color="channel",
                           title=f"Top {n} campaigns by {metric}").update_yaxes(autorange="reversed"),
                    use_container_width=True)
    st.plotly_chart(px.bar(kpi.by_type(df), x="campaign_type", y="ROI_%", title="ROI by campaign type"),
                    use_container_width=True)
    st.dataframe(cp.round(2), use_container_width=True)

# ---------------- Insights ----------------
with tab4:
    st.subheader("Business insights & recommendations")
    for i in insights.generate(df):
        st.markdown(f"- {i}")

# ---------------- Reports ----------------
with tab5:
    st.subheader("Downloadable reports")
    st.download_button("Marketing summary (.txt)", report.summary_text(df), "marketing_summary.txt")
    st.download_button("Campaign report (.csv)", report.campaign_report(df).to_csv(index=False),
                       "campaign_report.csv", "text/csv")
    st.download_button("Monthly analytics report (.csv)", report.monthly_report(df).to_csv(index=False),
                       "monthly_report.csv", "text/csv")
    xb = report.excel_bytes(df)
    if xb:
        st.download_button("Full workbook (.xlsx)", xb, "marketing_reports.xlsx")
    st.markdown("**Monthly preview**")
    st.dataframe(report.monthly_report(df), use_container_width=True)
