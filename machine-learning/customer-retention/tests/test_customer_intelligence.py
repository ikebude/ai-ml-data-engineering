import json
from pathlib import Path
from src.customer_intelligence import (
    BASE_DIR,
    load_and_clean_telco,
    run_all,
    run_rfm_and_clv_backtest,
)


def test_telco_loader_and_features():
    df = load_and_clean_telco()
    assert len(df) > 7000
    assert "target" in df.columns
    assert set(df["target"].unique()) == {0, 1}
    assert "tickets_total" in df.columns
    assert df["TotalCharges"].isna().sum() == 0


def test_full_customer_intelligence_pipeline():
    metrics = run_all()
    telco = metrics["telco_churn"]
    rfm = metrics["retail_rfm_clv"]

    assert telco["calibrated_gbdt"]["roc_auc"] >= 0.83
    assert telco["calibrated_gbdt"]["recall_at_20pct_budget"] >= 0.50
    assert rfm["churn_90d_roc_auc"] >= 0.72
    assert abs(rfm["clv_holdout_pct_error"]) <= 15.0

    assert (BASE_DIR / "reports" / "metrics.json").exists()
    assert (BASE_DIR / "reports" / "action_list.csv").exists()
    assert (BASE_DIR / "img" / "hero.png").exists()
