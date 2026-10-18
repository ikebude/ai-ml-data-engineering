"""Unit tests for the S&P 500 Financial Factor & Clustering pipeline."""

from pathlib import Path
import numpy as np

from src.pipeline import (
    CLUSTER_FEATURES,
    DATA_PATH,
    detect_robust_outliers,
    fit_pca_and_kmeans,
    load_and_engineer_features,
    run_pipeline,
)


def test_load_and_engineer_features_complete():
    df = load_and_engineer_features(DATA_PATH)
    assert len(df) == 502
    for col in CLUSTER_FEATURES:
        assert col in df.columns
        assert not df[col].isna().any(), f"NaN found in {col}"
        assert not np.isinf(df[col]).any(), f"Inf found in {col}"


def test_pca_and_clustering_bounds():
    df = detect_robust_outliers(load_and_engineer_features(DATA_PATH))
    clustered_df, meta, _ = fit_pca_and_kmeans(df)
    assert "cluster" in clustered_df.columns
    assert meta["optimal_k"] in (3, 4, 5, 6)
    assert 0.15 <= meta["silhouette_score"] <= 0.85
    assert 0.45 <= meta["pca_2d_cumulative_variance"] <= 0.95


def test_end_to_end_pipeline_outputs():
    report = run_pipeline(seed=42)
    rf_f1 = report["classification_benchmark"]["random_forest_classifier"]["macro_f1"]
    lr_f1 = report["classification_benchmark"]["logistic_regression_baseline"]["macro_f1"]
    assert rf_f1 > 0.60
    assert rf_f1 >= lr_f1

    project_dir = Path(__file__).resolve().parent.parent
    assert (project_dir / "reports" / "metrics.json").exists()
    assert (project_dir / "img" / "hero.png").exists()
