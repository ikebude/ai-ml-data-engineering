"""Streamlit dashboard for Customer Intelligence (Churn, RFM Segments & CLV)."""

import json
from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"

st.set_page_config(page_title="Customer Intelligence — Churn, RFM & CLV", layout="wide")
st.title("Customer Intelligence — Churn, Segments & Lifetime Value")
st.caption("Telco Subscription Churn (`N=7,043`) + Retail RFM Segmentation & 6-Month CLV Backtest")

metrics_path = REPORTS_DIR / "metrics.json"
action_path = REPORTS_DIR / "action_list.csv"
rfm_path = REPORTS_DIR / "rfm_segments.csv"

if not metrics_path.exists():
    from src.customer_intelligence import run_all
    run_all()

with open(metrics_path, "r", encoding="utf-8") as f:
    metrics = json.load(f)

telco = metrics["telco_churn"]
rfm = metrics["retail_rfm_clv"]

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Telco Churn ROC-AUC",
    f"{telco['calibrated_gbdt']['roc_auc']:.3f}",
    f"95% CI: {telco['calibrated_gbdt']['roc_auc_95ci'][0]:.3f}–{telco['calibrated_gbdt']['roc_auc_95ci'][1]:.3f}",
)
c2.metric(
    "Telco PR-AUC",
    f"{telco['calibrated_gbdt']['pr_auc']:.3f}",
    f"Recall@20% budget: {telco['calibrated_gbdt']['recall_at_20pct_budget']:.1%}",
)
c3.metric(
    "90-Day Retail Churn ROC-AUC",
    f"{rfm['churn_90d_roc_auc']:.3f}",
    f"Holdout CLV Error: {rfm['clv_holdout_pct_error']:+.2f}%",
)
c4.metric(
    "Top-50 12m Revenue at Risk",
    f"${telco['action_list_summary']['top_50_total_revenue_at_risk_usd']:,.0f}",
    f"Mean Churn Risk: {telco['action_list_summary']['top_50_mean_churn_prob']:.1%}",
)

tab1, tab2, tab3 = st.tabs(["Priority Retention Action List (Top 50)", "RFM Customer Segments", "Benchmark Metrics JSON"])

with tab1:
    st.subheader("Call These 50 Customers This Week (Ranked by 12m Revenue at Risk)")
    df_act = pd.read_csv(action_path)
    st.dataframe(df_act, use_container_width=True)
    st.download_button(
        "Download Top-50 Action List CSV",
        df_act.to_csv(index=False).encode("utf-8"),
        file_name="customer_intelligence_action_list.csv",
        mime="text/csv",
    )

with tab2:
    st.subheader("RFM Segments & 180-Day Predicted vs Actual Holdout CLV")
    df_rfm = pd.read_csv(rfm_path)
    st.bar_chart(df_rfm["segment"].value_counts())
    st.dataframe(df_rfm.head(100), use_container_width=True)

with tab3:
    st.json(metrics)
