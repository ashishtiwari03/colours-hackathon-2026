import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from utils.insight_engine import load_survey, team_dimension_means, detect_risks, company_summary
from utils.trend_data import build_historical_trend, build_projection, roi_calculation

st.set_page_config(page_title="PulseAct", page_icon="📊", layout="wide")


@st.cache_data
def load_recommendations() -> list[dict]:
    path = Path("data/recommendations_cache.json")
    return json.loads(path.read_text(encoding="utf-8"))


with st.sidebar:
    st.title("📊 PulseAct")
    st.caption("From Survey to Action")
    st.divider()
    st.markdown("**COLOURS Hackathon 2026**")
    st.markdown("_Workplace Reinvented Challenge #7_")
    st.divider()
    st.caption("Demo: MetalWorks Latvia, 100 employees")

tab1, tab2, tab3 = st.tabs(["📥 Upload & Insights", "🎯 Action Plan", "📈 Trend & ROI"])

with tab1:
    st.subheader("Upload your wellbeing survey")

    uploaded = st.file_uploader("Upload CSV", type=["csv"], help="Or use the demo dataset below")

    if uploaded is not None:
        df = pd.read_csv(uploaded)
        st.caption(f"✓ Loaded {len(df)} responses from your file")
    else:
        df = load_survey()
        st.caption("Using demo data: MetalWorks Latvia (100 employees, 5 teams)")

    st.divider()

    summary = company_summary(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Employees", summary["total_employees"])
    col2.metric("Teams", summary["num_teams"])
    col3.metric(
        "Overall Wellbeing",
        f'{summary["overall_mean_excluding_burnout"]:.2f}',
        help="Average across 7 positive dimensions (1-5, higher is better)",
    )
    col4.metric(
        "Burnout Risk",
        f'{summary["overall_burnout_mean"]:.2f}',
        help="Average burnout signal (1-5, lower is better)",
    )

    st.info(
        "📊 **At first glance, MetalWorks looks fine.** "
        "Overall wellbeing 3.27, burnout 3.44 — manageable averages. "
        "But averages hide where the real problem is. Scroll down."
    )

    st.divider()

    st.subheader("🌡️ Risk heatmap by team")

    means_long = team_dimension_means(df)
    pivot = means_long.pivot(index="team", columns="dimension", values="mean_score")

    positive_dims = [
        "workload_manageability", "recognition", "communication",
        "manager_support", "growth", "autonomy", "social_connection",
    ]
    column_order = positive_dims + ["burnout_risk"]
    pivot = pivot[column_order]

    display_pivot = pivot.copy()
    display_pivot["burnout_risk"] = 6 - display_pivot["burnout_risk"]
    display_pivot = display_pivot.rename(columns={"burnout_risk": "burnout_risk*"})

    fig = px.imshow(
        display_pivot,
        text_auto=".2f",
        color_continuous_scale="RdYlGn",
        zmin=1,
        zmax=5,
        aspect="auto",
        labels={"color": "Score"},
    )
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=True,
    )
    fig.update_xaxes(side="bottom", tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("*burnout_risk inverted for visualization (red = high risk)")

    st.divider()

    st.subheader("🚨 Top risk patterns")
    risks = detect_risks(df, top_n=5)

    for risk in risks:
        with st.container(border=True):
            cols = st.columns([2, 2, 1, 1])
            cols[0].markdown(f"**{risk['team']}**")
            cols[1].markdown(f"`{risk['dimension']}`")
            score_color = "🔴" if risk["severity"] >= 0.5 else "🟠"
            cols[2].markdown(f"{score_color} **{risk['mean_score']:.2f}**")
            cols[3].caption(f"{risk['employee_count']} employees")

with tab2:
    st.subheader("🎯 Action Plan for Leadership")
    st.caption(
        "Top 5 risks identified. Each comes with AI-generated recommendations "
        "tailored to a Latvian manufacturing context. Click any card to expand."
    )

    recommendations = load_recommendations()

    all_teams = sorted({r["team"] for r in recommendations})
    selected = st.radio(
        "Filter by team",
        ["All"] + all_teams,
        horizontal=True,
        label_visibility="collapsed",
    )

    if selected and selected != "All":
        filtered = [r for r in recommendations if r["team"] == selected]
    else:
        filtered = recommendations

    if not filtered:
        st.info("No risks for this filter.")

    for i, rec in enumerate(filtered):
        if rec["severity"] >= 0.6:
            icon = "🔴"
            severity_label = "CRITICAL"
        elif rec["severity"] >= 0.4:
            icon = "🟠"
            severity_label = "HIGH"
        else:
            icon = "🟡"
            severity_label = "MODERATE"

        title = f"{icon}  **{rec['team']}** / `{rec['dimension']}` — score {rec['mean_score']:.2f} ({rec['employee_count']} employees) — {severity_label}"

        with st.expander(title, expanded=(i == 0)):
            st.markdown(f"### {rec['headline']}")
            st.markdown(f"**Why it matters:** {rec['why_it_matters']}")

            st.divider()
            st.markdown("**Recommended actions:**")

            for j, action in enumerate(rec["actions"], start=1):
                with st.container(border=True):
                    cols = st.columns([5, 1, 1, 1])
                    cols[0].markdown(f"**{j}.** {action['action']}")
                    cols[1].caption(f"Effort: **{action['effort']}**")
                    cols[2].caption(f"Impact: **{action['impact']}**")
                    cols[3].caption(f"⏱ {action['timeline_weeks']}w")

    st.divider()
    st.caption(
        "ℹ️ Pattern detection runs deterministically (pandas). "
        "Recommendations generated by Mistral AI, cached locally for demo reliability."
    )

with tab3:
    st.subheader("📈 Trend & ROI")
    st.caption(
        "How wellbeing trended over the last 6 months, what improvement we expect "
        "from acting on the recommendations, and what it's worth in euros."
    )

    # Section 1 — Historical trend
    st.markdown("### 6-month wellbeing trend by team")

    historical = build_historical_trend()
    fig_trend = px.line(
        historical,
        x="month",
        y="wellbeing_score",
        color="team",
        markers=True,
        labels={"wellbeing_score": "Wellbeing score (1-5)", "month": ""},
    )
    fig_trend.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(range=[2.5, 4.0], title="Wellbeing score"),
    )
    fig_trend.update_traces(line=dict(width=2))
    for trace in fig_trend.data:
        if trace.name == "Production":
            trace.line.width = 4
            trace.line.color = "#e74c3c"
    st.plotly_chart(fig_trend, use_container_width=True)

    st.info(
        "📉 **Production team has been declining for 6 months.** "
        "This was visible in survey data all along — PulseAct surfaces it as actionable insight."
    )

    st.divider()

    # Section 2 — Projection
    st.markdown("### Predicted improvement: Production team, 12 weeks")
    st.caption("If leadership acts on the top 3 AI-recommended actions per dimension.")

    projection = build_projection()

    # Show only the top 4 dimensions with largest current-vs-projected gap
    projection_display = projection.copy()
    # For burnout_risk, the gap is current - projected (improvement = decrease)
    # For others, gap is projected - current (improvement = increase)
    projection_display["gap"] = projection_display.apply(
        lambda r: r["current_score"] - r["projected_score"]
                  if r["dimension"] == "burnout_risk"
                  else r["projected_score"] - r["current_score"],
        axis=1,
    )
    projection_display = projection_display.nlargest(4, "gap").reset_index(drop=True)

    fig_proj = go.Figure()
    fig_proj.add_trace(go.Bar(
        name="Current",
        x=projection_display["dimension"],
        y=projection_display["current_score"],
        marker_color="#e74c3c",
    ))
    fig_proj.add_trace(go.Bar(
        name="After 12 weeks",
        x=projection_display["dimension"],
        y=projection_display["projected_score"],
        marker_color="#27ae60",
    ))
    fig_proj.update_layout(
        barmode="group",
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(range=[0, 5], title="Score (1-5)"),
        xaxis=dict(tickangle=0),
    )
    st.plotly_chart(fig_proj, use_container_width=True)
    st.caption("Showing the 4 dimensions with biggest projected improvement. Burnout risk: lower is better (projected to drop from 4.25 to 3.20).")

    st.divider()

    # Section 3 — ROI
    st.markdown("### 💰 Return on Investment")
    st.caption("For a 100-employee Latvian manufacturing company.")

    roi = roi_calculation(company_size=100)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Annual cost of inaction",
        f"€{roi['annual_inaction_cost']:,}",
        help="Estimated burnout-driven resignations × replacement cost",
    )
    col2.metric(
        "PulseAct annual cost",
        f"€{roi['pulseact_annual_cost']:,}",
        help="€500/month SaaS pricing",
    )
    col3.metric(
        "Net annual savings",
        f"€{roi['net_savings']:,}",
        delta=f"€{roi['net_savings']:,}",
        delta_color="normal",
    )
    col4.metric(
        "Payback period",
        f"{roi['payback_months']} months",
        help="How long until the tool pays for itself",
    )

    st.success(
        f"💡 **Bottom line:** PulseAct pays for itself in {roi['payback_months']} months. "
        f"Preventing even one burnout-driven resignation covers the full year's cost."
    )

    st.divider()

    # Section 4 — Model assumptions
    with st.expander("📋 Model assumptions"):
        st.markdown("""
        - **Replacement cost:** €12,000 per employee (Baltic manufacturing average, includes recruitment, onboarding, ramp-up productivity loss).
        - **Resignation rate:** 1.5 burnout-driven resignations per year per 100 employees among at-risk teams.
        - **PulseAct pricing:** €500/month SaaS, scales with company size.
        - **Projection accuracy:** Based on published return-to-engagement studies. Real outcomes vary by execution quality.
        - **Historical data:** Synthesized for demo. Real deployment uses your existing survey data.
        """)
