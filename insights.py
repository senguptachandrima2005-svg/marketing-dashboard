"""Module 4: Business insights & recommendations (rule-based, no ML)."""
import pandas as pd
import kpi


def generate(df: pd.DataFrame) -> list[str]:
    out = []
    ch = kpi.by_channel(df)
    cp = kpi.by_campaign(df)
    ty = kpi.by_type(df)
    tot = kpi.overall(df)

    best = ch.sort_values("ROI_%", ascending=False).iloc[0]
    worst = ch.sort_values("ROI_%").iloc[0]
    conv = ch.sort_values("Conv_Rate_%", ascending=False).iloc[0]
    eng = ch.sort_values("Engagement_Rate_%", ascending=False).iloc[0]
    cheap = ch.sort_values("CPA").iloc[0]
    top_c = cp.sort_values("ROI_%", ascending=False).iloc[0]
    bot_c = cp.sort_values("ROI_%").iloc[0]
    best_t = ty.sort_values("ROI_%", ascending=False).iloc[0]

    out.append(f"Overall, ${tot['spend']:,.0f} of spend produced ${tot['revenue']:,.0f} in revenue "
               f"(ROI {tot['ROI_%']:.0f}%, ROAS {tot['ROAS']:.2f}x).")
    out.append(f"Highest-ROI channel: {best['channel']} ({best['ROI_%']:.0f}% ROI). "
               f"Consider shifting budget toward it.")
    out.append(f"Lowest-ROI channel: {worst['channel']} ({worst['ROI_%']:.0f}% ROI). "
               f"Review targeting and creatives before further spend.")
    out.append(f"Highest-converting channel: {conv['channel']} ({conv['Conv_Rate_%']:.1f}% click-to-conversion).")
    out.append(f"Lowest cost per acquisition: {cheap['channel']} (${cheap['CPA']:.2f} per conversion).")
    out.append(f"Best audience engagement: {eng['channel']} ({eng['Engagement_Rate_%']:.2f}% of impressions).")
    out.append(f"Best-performing campaign: {top_c['campaign_name']} on {top_c['channel']} "
               f"(ROI {top_c['ROI_%']:.0f}%). Replicate its creative and audience.")
    out.append(f"Weakest campaign: {bot_c['campaign_name']} on {bot_c['channel']} "
               f"(ROI {bot_c['ROI_%']:.0f}%). Pause or rework.")
    out.append(f"Best campaign type: {best_t['campaign_type']} (ROI {best_t['ROI_%']:.0f}%).")

    w = kpi.trend(df, "W")
    w = w.iloc[:-1] if len(w) > 1 else w  # drop possibly incomplete last week
    if len(w) >= 8:
        recent, prev = w.tail(4)["revenue"].sum(), w.iloc[-8:-4]["revenue"].sum()
        if prev:
            chg = (recent - prev) / prev * 100
            out.append(f"Revenue over the last 4 weeks is {'up' if chg >= 0 else 'down'} {abs(chg):.1f}% vs. the prior 4 weeks.")
    return out
