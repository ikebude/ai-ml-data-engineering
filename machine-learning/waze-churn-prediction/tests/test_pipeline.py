"""Unit tests for the Waze User Churn Prediction pipeline."""

from pathlib import Path
import numpy as np
import pandas as pd

from src.pipeline import (
    DATA_PATH,
    FEATURE_COLS,
    engineer_features,
    load_and_clean_data,
    recall_at_k,
    run_pipeline,
)


def test_load_and_clean_data_drops_missing_labels():
    df = load_and_clean_data(DATA_PATH)
    assert len(df) == 14299
    assert df["label"].isna().sum() == 0
    assert set(df["target"].unique()) == {0, 1}
    assert 0.17 < df["target"].mean() < 0.18


def test_feature_engineering_no_leakage_or_nans():
    df = engineer_features(load_and_clean_data(DATA_PATH))
    for col in FEATURE_COLS:
        assert col in df.columns, f"Missing feature column {col}"
        assert not df[col].isna().any(), f"NaN found in {col}"
        assert not np.isinf(df[col]).any(), f"Inf found in {col}"
    assert "label" not in FEATURE_COLS
    assert "target" not in FEATURE_COLS
    assert "ID" not in FEATURE_COLS


def test_recall_at_k_bounds():
    y_true = np.array([1, 1, 0, 0, 1, 0, 0, 0, 0, 0])
    y_score = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05])
    r20 = recall_at_k(y_true, y_score, 0.20)
    assert np.isclose(r20, 2 / 3)


def test_end_to_end_pipeline_metrics_and_artifacts():
    report = run_pipeline(seed=42)
    hgb = report["models"]["calibrated_hist_gradient_boosting"]["point"]
    lr = report["models"]["logistic_regression_baseline"]["point"]

    assert 0.35 <= hgb["pr_auc"] <= 0.60
    assert 0.70 <= hgb["roc_auc"] <= 0.85
    assert 0.20 <= hgb["recall_at_10pct"] <= 0.45
    assert 0.40 <= hgb["recall_at_20pct"] <= 0.65
    assert 0.35 <= lr["pr_auc"] <= 0.60

    project_dir = Path(__file__).resolve().parent.parent
    assert (project_dir / "reports" / "metrics.json").exists()
    assert (project_dir / "img" / "hero.png").exists()
