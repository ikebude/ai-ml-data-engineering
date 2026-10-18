from src.loanlens import (
    BASE_DIR,
    LEAKAGE_COLUMNS,
    NUM_FEATURES,
    CAT_FEATURES,
    load_closed_loans,
    pd_to_credit_score,
    run_all,
)
import numpy as np


def test_no_leakage_columns():
    used = set(NUM_FEATURES + CAT_FEATURES)
    assert LEAKAGE_COLUMNS.isdisjoint(used)


def test_credit_score_monotonic():
    pds = np.array([0.02, 0.10, 0.25, 0.50])
    scores = pd_to_credit_score(pds)
    assert np.all(np.diff(scores) < 0)
    assert np.all((scores >= 300) & (scores <= 850))


def test_loanlens_out_of_time_pipeline():
    metrics = run_all()
    assert metrics["total_closed_loans"] > 50000
    assert metrics["calibrated_gbdt_ensemble"]["roc_auc"] >= 0.70
    assert metrics["calibrated_gbdt_ensemble"]["ks_statistic"] >= 0.30
    assert metrics["calibrated_gbdt_ensemble"]["ece"] <= 0.08
    assert (BASE_DIR / "reports" / "metrics.json").exists()
    assert (BASE_DIR / "reports" / "policy_curve.csv").exists()
    assert (BASE_DIR / "img" / "hero.png").exists()
