"""
NYC TLC Yellow Taxi Pre-Trip Fare & Duration Intelligence Pipeline.

Loads 2017_Yellow_Taxi_Trip_Data.csv (22,699 trips), cleans anomalous records
(fare_amount > 0, trip_distance > 0, positive duration), extracts strictly pre-trip
features (excluding post-trip total_amount, tip_amount, tolls_amount, extra,
mta_tax, improvement_surcharge, payment_type, and tpep_dropoff_datetime to prevent
target leakage), orders trips chronologically by tpep_pickup_datetime for an 80/20
out-of-time split, benchmarks Linear Ridge against HistGradientBoostingRegressor
for both fare_amount ($) and trip_duration_min (minutes), computes MAE, RMSE, and R2
with 95% bootstrap CIs, writes reports/metrics.json, and renders monochrome/emerald
charts in img/.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "2017_Yellow_Taxi_Trip_Data.csv"
REPORTS_DIR = PROJECT_DIR / "reports"
IMG_DIR = PROJECT_DIR / "img"

PRE_TRIP_FEATURES = [
    "trip_distance",
    "pickup_hour",
    "pickup_dayofweek",
    "is_weekend",
    "is_rush_hour",
    "RatecodeID",
    "PULocationID",
    "DOLocationID",
    "passenger_count",
]

FORBIDDEN_POST_TRIP_COLUMNS = {
    "total_amount",
    "tip_amount",
    "tolls_amount",
    "extra",
    "mta_tax",
    "improvement_surcharge",
    "payment_type",
    "tpep_dropoff_datetime",
    "fare_amount",
    "trip_duration_min",
}


def load_and_clean_data(csv_path: Path = DATA_PATH) -> pd.DataFrame:
    """Load NYC TLC taxi trips, parse timestamps, and filter invalid fare/distance anomalies."""
    df = pd.read_csv(csv_path)
    df["pickup_dt"] = pd.to_datetime(df["tpep_pickup_datetime"], format="%m/%d/%Y %I:%M:%S %p")
    df["dropoff_dt"] = pd.to_datetime(df["tpep_dropoff_datetime"], format="%m/%d/%Y %I:%M:%S %p")
    df["trip_duration_min"] = (df["dropoff_dt"] - df["pickup_dt"]).dt.total_seconds() / 60.0

    # Filter anomalous trips: require positive fare, positive distance, reasonable duration & fare
    mask = (
        (df["fare_amount"] > 0)
        & (df["fare_amount"] <= 250.0)
        & (df["trip_distance"] > 0)
        & (df["trip_distance"] <= 100.0)
        & (df["trip_duration_min"] > 0.5)
        & (df["trip_duration_min"] <= 180.0)
        & (df["RatecodeID"].isin([1, 2, 3, 4, 5]))
    )
    clean_df = df.loc[mask].copy()
    clean_df = clean_df.sort_values("pickup_dt").reset_index(drop=True)
    return clean_df


def engineer_pre_trip_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract strictly pre-trip dispatch features without post-trip leakage."""
    out = df.copy()
    out["pickup_hour"] = out["pickup_dt"].dt.hour
    out["pickup_dayofweek"] = out["pickup_dt"].dt.dayofweek
    out["is_weekend"] = (out["pickup_dayofweek"] >= 5).astype(int)
    out["is_rush_hour"] = (
        (out["is_weekend"] == 0)
        & (out["pickup_hour"].isin([7, 8, 9, 16, 17, 18, 19]))
    ).astype(int)
    return out


def chronological_split(
    df: pd.DataFrame, train_frac: float = 0.80
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Perform an 80/20 chronological split ordered by pickup_dt."""
    ordered = df.sort_values("pickup_dt").reset_index(drop=True)
    split_idx = int(np.floor(len(ordered) * train_frac))
    return ordered.iloc[:split_idx].copy(), ordered.iloc[split_idx:].copy()


def bootstrap_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_boot: int = 500,
    seed: int = 42,
) -> dict[str, Any]:
    """Compute MAE, RMSE, and R2 point estimates and 95% bootstrap CIs."""
    rng = np.random.default_rng(seed)
    n = len(y_true)

    point = {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }

    samples: dict[str, list[float]] = {k: [] for k in point}
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        yt = y_true[idx]
        yp = y_pred[idx]
        samples["mae"].append(float(mean_absolute_error(yt, yp)))
        samples["rmse"].append(float(np.sqrt(mean_squared_error(yt, yp))))
        samples["r2"].append(float(r2_score(yt, yp)))

    ci_95 = {
        k: [
            round(float(np.percentile(v, 2.5)), 4),
            round(float(np.percentile(v, 97.5)), 4),
        ]
        for k, v in samples.items()
    }
    return {
        "point": {k: round(v, 4) for k, v in point.items()},
        "ci_95": ci_95,
    }


def render_charts(
    test_df: pd.DataFrame,
    fare_pred_hgb: np.ndarray,
    fare_pred_ridge: np.ndarray,
    dur_pred_hgb: np.ndarray,
    img_dir: Path = IMG_DIR,
) -> None:
    """Render monochrome + emerald portfolio figures (1600x900 hero and 1200x1200 square)."""
    img_dir.mkdir(parents=True, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9), dpi=100, facecolor="#0B0B0C")
    for ax in (ax1, ax2):
        ax.set_facecolor("#121215")
        ax.tick_params(colors="#D4D4D8", labelsize=10)
        for spine in ax.spines.values():
            spine.set_color("#2A2A2E")
        ax.grid(True, color="#222226", linestyle="--", linewidth=0.7, alpha=0.8)

    y_fare = test_df["fare_amount"].to_numpy()
    max_val = 75.0
    mask_plot = y_fare <= max_val

    ax1.scatter(
        y_fare[mask_plot],
        fare_pred_ridge[mask_plot],
        color="#52525B",
        alpha=0.25,
        s=14,
        label="Linear Ridge Baseline",
    )
    ax1.scatter(
        y_fare[mask_plot],
        fare_pred_hgb[mask_plot],
        color="#10B981",
        alpha=0.35,
        s=14,
        label="HistGradientBoosting (Pre-Trip)",
    )
    ax1.plot([0, max_val], [0, max_val], color="#F4F4F5", linestyle="--", linewidth=1.4, label="Ideal 1:1")
    ax1.set_xlim(0, max_val)
    ax1.set_ylim(0, max_val)
    ax1.set_title(
        "Out-of-Time Fare Prediction ($ USD, Test Split)",
        color="#F4F4F5",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax1.set_xlabel("Actual Metered Fare ($)", color="#D4D4D8", fontsize=11)
    ax1.set_ylabel("Predicted Pre-Trip Fare ($)", color="#D4D4D8", fontsize=11)
    ax1.legend(facecolor="#18181B", edgecolor="#2A2A2E", labelcolor="#E4E4E7", fontsize=9.5)

    # Right panel: Mean Fare & Trip Duration by Pickup Hour on Test Split
    hourly = (
        test_df.assign(pred_fare=fare_pred_hgb, pred_dur=dur_pred_hgb)
        .groupby("pickup_hour", as_index=False)
        .agg(
            actual_fare=("fare_amount", "mean"),
            pred_fare=("pred_fare", "mean"),
            actual_dur=("trip_duration_min", "mean"),
            pred_dur=("pred_dur", "mean"),
        )
    )
    ax2.plot(
        hourly["pickup_hour"],
        hourly["actual_dur"],
        color="#A1A1AA",
        marker="o",
        linewidth=1.8,
        label="Actual Mean Duration (min)",
    )
    ax2.plot(
        hourly["pickup_hour"],
        hourly["pred_dur"],
        color="#10B981",
        marker="s",
        linewidth=2.4,
        label="Predicted Mean Duration (min)",
    )
    ax2.set_title(
        "Diurnal Congestion Profile: Actual vs Predicted Duration by Pickup Hour",
        color="#F4F4F5",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax2.set_xlabel("Pickup Hour of Day (0–23h NYC Local)", color="#D4D4D8", fontsize=11)
    ax2.set_ylabel("Mean Trip Duration (Minutes)", color="#D4D4D8", fontsize=11)
    ax2.set_xticks(range(0, 24, 2))
    ax2.legend(facecolor="#18181B", edgecolor="#2A2A2E", labelcolor="#E4E4E7", fontsize=9.5)

    fig.suptitle(
        "NYC TLC Cab Fare Intelligence · Out-of-Time Pre-Trip Estimation",
        color="#FFFFFF",
        fontsize=16,
        fontweight="bold",
        y=0.97,
    )
    fig.tight_layout(rect=[0, 0.02, 1, 0.93])
    fig.savefig(img_dir / "hero.png", dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)

    # Square image for social posts (1200x1200)
    fig_sq, ax_sq = plt.subplots(figsize=(12, 12), dpi=100, facecolor="#0B0B0C")
    ax_sq.set_facecolor("#121215")
    ax_sq.tick_params(colors="#D4D4D8", labelsize=11)
    for spine in ax_sq.spines.values():
        spine.set_color("#2A2A2E")
    ax_sq.grid(True, color="#222226", linestyle="--", linewidth=0.8, alpha=0.8)

    residuals_ridge = np.abs(y_fare - fare_pred_ridge)
    residuals_hgb = np.abs(y_fare - fare_pred_hgb)
    bins = np.linspace(0, 8, 33)
    ax_sq.hist(
        np.clip(residuals_ridge, 0, 8),
        bins=bins,
        alpha=0.55,
        color="#52525B",
        label=f"Linear Ridge (MAE = ${np.mean(residuals_ridge):.2f})",
    )
    ax_sq.hist(
        np.clip(residuals_hgb, 0, 8),
        bins=bins,
        alpha=0.75,
        color="#10B981",
        label=f"HistGradientBoosting (MAE = ${np.mean(residuals_hgb):.2f})",
    )
    ax_sq.set_title(
        "Absolute Fare Error Distribution ($ USD, Out-of-Time Test Split)",
        color="#FFFFFF",
        fontsize=15,
        fontweight="bold",
        pad=15,
    )
    ax_sq.set_xlabel("Absolute Fare Prediction Error |Actual - Predicted| ($)", color="#D4D4D8", fontsize=12)
    ax_sq.set_ylabel("Number of Test Trips", color="#D4D4D8", fontsize=12)
    ax_sq.legend(facecolor="#18181B", edgecolor="#2A2A2E", labelcolor="#E4E4E7", fontsize=11)
    fig_sq.tight_layout()
    fig_sq.savefig(img_dir / "post_square.png", dpi=100, facecolor=fig_sq.get_facecolor())
    plt.close(fig_sq)


def run_pipeline(seed: int = 42) -> dict[str, Any]:
    """Run NYC TLC pre-trip fare & duration pipeline and write reports/metrics.json."""
    raw_df = pd.read_csv(DATA_PATH)
    n_raw = len(raw_df)
    n_nonpositive_fare = int((raw_df["fare_amount"] <= 0).sum())
    n_zero_distance = int((raw_df["trip_distance"] <= 0).sum())

    clean_df = load_and_clean_data(DATA_PATH)
    feat_df = engineer_pre_trip_features(clean_df)

    train_df, test_df = chronological_split(feat_df, train_frac=0.80)

    X_train = train_df[PRE_TRIP_FEATURES].to_numpy(dtype=float)
    X_test = test_df[PRE_TRIP_FEATURES].to_numpy(dtype=float)

    y_fare_train = train_df["fare_amount"].to_numpy(dtype=float)
    y_fare_test = test_df["fare_amount"].to_numpy(dtype=float)

    y_dur_train = train_df["trip_duration_min"].to_numpy(dtype=float)
    y_dur_test = test_df["trip_duration_min"].to_numpy(dtype=float)

    # Fare amount models
    ridge_fare = Pipeline(
        [("scaler", StandardScaler()), ("reg", Ridge(alpha=10.0, random_state=seed))]
    )
    ridge_fare.fit(X_train, y_fare_train)
    pred_fare_ridge = ridge_fare.predict(X_test)

    hgb_fare = HistGradientBoostingRegressor(
        max_iter=250,
        learning_rate=0.06,
        max_leaf_nodes=31,
        min_samples_leaf=25,
        l2_regularization=1.0,
        random_state=seed,
    )
    hgb_fare.fit(X_train, y_fare_train)
    pred_fare_hgb = hgb_fare.predict(X_test)

    # Trip duration models
    ridge_dur = Pipeline(
        [("scaler", StandardScaler()), ("reg", Ridge(alpha=10.0, random_state=seed))]
    )
    ridge_dur.fit(X_train, y_dur_train)
    pred_dur_ridge = ridge_dur.predict(X_test)

    hgb_dur = HistGradientBoostingRegressor(
        max_iter=250,
        learning_rate=0.06,
        max_leaf_nodes=31,
        min_samples_leaf=25,
        l2_regularization=1.0,
        random_state=seed,
    )
    hgb_dur.fit(X_train, y_dur_train)
    pred_dur_hgb = hgb_dur.predict(X_test)

    fare_ridge_metrics = bootstrap_regression_metrics(y_fare_test, pred_fare_ridge, n_boot=500, seed=seed)
    fare_hgb_metrics = bootstrap_regression_metrics(y_fare_test, pred_fare_hgb, n_boot=500, seed=seed)
    dur_ridge_metrics = bootstrap_regression_metrics(y_dur_test, pred_dur_ridge, n_boot=500, seed=seed)
    dur_hgb_metrics = bootstrap_regression_metrics(y_dur_test, pred_dur_hgb, n_boot=500, seed=seed)

    render_charts(test_df, pred_fare_hgb, pred_fare_ridge, pred_dur_hgb, IMG_DIR)

    within_1_dollar_ridge = round(float(np.mean(np.abs(y_fare_test - pred_fare_ridge) <= 1.0)), 4)
    within_1_dollar_hgb = round(float(np.mean(np.abs(y_fare_test - pred_fare_hgb) <= 1.0)), 4)
    within_2_dollars_hgb = round(float(np.mean(np.abs(y_fare_test - pred_fare_hgb) <= 2.0)), 4)

    report = {
        "dataset": {
            "total_raw_rows": n_raw,
            "anomalous_nonpositive_fare_rows": n_nonpositive_fare,
            "anomalous_zero_distance_rows": n_zero_distance,
            "clean_rows": len(feat_df),
            "train_rows": len(train_df),
            "test_rows": len(test_df),
            "train_period_start": str(train_df["pickup_dt"].min()),
            "train_period_end": str(train_df["pickup_dt"].max()),
            "test_period_start": str(test_df["pickup_dt"].min()),
            "test_period_end": str(test_df["pickup_dt"].max()),
            "mean_fare_usd": round(float(feat_df["fare_amount"].mean()), 2),
            "median_fare_usd": round(float(feat_df["fare_amount"].median()), 2),
            "mean_distance_miles": round(float(feat_df["trip_distance"].mean()), 2),
            "mean_duration_min": round(float(feat_df["trip_duration_min"].mean()), 2),
        },
        "pre_trip_features": PRE_TRIP_FEATURES,
        "fare_amount_models": {
            "linear_ridge_baseline": fare_ridge_metrics,
            "hist_gradient_boosting": fare_hgb_metrics,
            "within_1_usd_rate_ridge": within_1_dollar_ridge,
            "within_1_usd_rate_hgb": within_1_dollar_hgb,
            "within_2_usd_rate_hgb": within_2_dollars_hgb,
        },
        "trip_duration_min_models": {
            "linear_ridge_baseline": dur_ridge_metrics,
            "hist_gradient_boosting": dur_hgb_metrics,
        },
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    results = run_pipeline()
    print(json.dumps(results, indent=2))
