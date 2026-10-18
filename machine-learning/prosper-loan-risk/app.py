"""Streamlit app for LoanLens — Credit Risk Scorecard & Approval Policy Simulator."""

import json
from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"

st.set_page_config(page_title="LoanLens — Credit Risk & Policy Simulator", layout="wide")
st.title("LoanLens — Credit Risk Scorecard & Policy Simulator")
st.caption("Out-of-Time Prosper Loan Default Evaluation (`WoE Scorecard + Calibrated GBDT`)")

metrics_path = REPORTS_DIR / "metrics.json"
policy_path = REPORTS_DIR / "policy_curve.csv"

if not metrics_path.exists():
    from src.loanlens import run_all
    run_all()

with open(metrics_path, "r", encoding="utf-8") as f:
    metrics = json.load(f)

ens = metrics["calibrated_gbdt_ensemble"]
rec = metrics["recommended_policy_at_25pct_pd"]

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Out-of-Time ROC-AUC",
    f"{ens['roc_auc']:.3f}",
    f"95% CI: {ens['roc_auc_95ci'][0]:.3f}–{ens['roc_auc_95ci'][1]:.3f}",
)
c2.metric("Out-of-Time KS Statistic", f"{ens['ks_statistic']:.3f}", f"ECE: {ens['ece']:.4f}")
c3.metric(
    "Approval Rate @ 25% Max PD",
    f"{rec['approval_rate']:.1%}",
    f"Min Score: {rec['min_credit_score']}",
)
c4.metric(
    "Net Portfolio Yield @ 25% PD",
    f"{rec['net_expected_yield']:.2%}",
    f"Bad Rate: {rec['observed_default_rate']:.2%}",
)

tab1, tab2, tab3 = st.tabs(["Approval Policy Simulator", "Fairness & Slice Audit", "Raw Metrics JSON"])

with tab1:
    st.subheader("Interactive Policy Cutoff Simulator (Out-of-Time Test Cohort)")
    df_pol = pd.read_csv(policy_path)
    st.dataframe(df_pol, use_container_width=True)

with tab2:
    st.subheader("Homeowner vs Non-Homeowner Underwriting Slice Audit (at 25% Max PD)")
    st.json(metrics["fairness_homeowner_slice"])
    st.info(
        "Governance Note: This model is trained on US peer-to-peer loan records (Prosper). "
        "Before deployment in Nigerian or emerging-market lending, scorecards must be recalibrated on local bureau and repayment history."
    )

with tab3:
    st.json(metrics)
