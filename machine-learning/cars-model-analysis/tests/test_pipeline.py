"""Unit tests for the Automotive Hedonic Pricing & Efficiency pipeline."""

from pathlib import Path
import numpy as np

from src.pipeline import (
    ALL_FEATURES,
    DATA_PATH,
    FORBIDDEN_LEAKAGE_FEATURES,
    load_and_clean_data,
    run_pipeline,
)


def test_currency_parsing_and_imputation():
    df = load_and_clean_data(DATA_PATH)
    assert len(df) == 428
    assert not df["MSRP_num"].isna().any()
    assert not df["Invoice_num"].isna().any()
    assert not df["Cylinders"].isna().any()
    assert (df["MSRP_num"] >= df["Invoice_num"]).all()


def test_no_invoice_leakage_in_pricing_features():
    for col in ALL_FEATURES:
        assert col not in FORBIDDEN_LEAKAGE_FEATURES, f"Leaked column {col} found in ALL_FEATURES"


def test_end_to_end_pipeline_metrics_and_artifacts():
    report = run_pipeline(seed=42)
    gbr = report["models"]["gradient_boosting_regressor"]["point"]
    ridge = report["models"]["log_ridge_baseline"]["point"]

    assert gbr["r2"] > 0.80
    assert gbr["mape"] < 0.16
    assert gbr["mae"] < ridge["mae"]

    project_dir = Path(__file__).resolve().parent.parent
    assert (project_dir / "reports" / "metrics.json").exists()
    assert (project_dir / "img" / "hero.png").exists()
