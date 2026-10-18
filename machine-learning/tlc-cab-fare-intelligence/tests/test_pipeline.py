"""Unit tests for NYC TLC Cab Fare & Duration Intelligence pipeline."""

from pathlib import Path

from src.pipeline import (
    DATA_PATH,
    FORBIDDEN_POST_TRIP_COLUMNS,
    PRE_TRIP_FEATURES,
    chronological_split,
    engineer_pre_trip_features,
    load_and_clean_data,
    run_pipeline,
)


def test_clean_data_removes_anomalies():
    df = load_and_clean_data(DATA_PATH)
    assert len(df) > 22000
    assert (df["fare_amount"] > 0).all()
    assert (df["trip_distance"] > 0).all()
    assert (df["trip_duration_min"] > 0.5).all()


def test_no_post_trip_leakage_in_features():
    for col in PRE_TRIP_FEATURES:
        assert col not in FORBIDDEN_POST_TRIP_COLUMNS, f"Leaked column {col} found in PRE_TRIP_FEATURES"


def test_chronological_split_is_strictly_out_of_time():
    df = engineer_pre_trip_features(load_and_clean_data(DATA_PATH))
    train_df, test_df = chronological_split(df, train_frac=0.80)
    assert len(train_df) + len(test_df) == len(df)
    assert train_df["pickup_dt"].max() <= test_df["pickup_dt"].min()


def test_end_to_end_pipeline_metrics_and_artifacts():
    report = run_pipeline(seed=42)
    hgb_fare = report["fare_amount_models"]["hist_gradient_boosting"]["point"]
    ridge_fare = report["fare_amount_models"]["linear_ridge_baseline"]["point"]

    assert hgb_fare["mae"] < ridge_fare["mae"]
    assert hgb_fare["r2"] > 0.85
    assert hgb_fare["mae"] < 1.80

    project_dir = Path(__file__).resolve().parent.parent
    assert (project_dir / "reports" / "metrics.json").exists()
    assert (project_dir / "img" / "hero.png").exists()
