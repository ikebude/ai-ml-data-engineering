"""
Automotive Hedonic Pricing & Powertrain Efficiency Pipeline.

Loads CarsDataset.csv (428 vehicles), parses currency strings ('$' and ',') from MSRP
and Invoice, imputes missing Cylinders (rotary engines) by EngineSize median, engineers
power_to_weight, mpg_combined (EPA 55/45 harmonic-weighted city/highway formula), and
dealer_margin_pct, and trains a Ridge baseline vs GradientBoostingRegressor hedonic
pricing model to predict MSRP from physical specs + Origin + Type + DriveTrain
(strictly excluding Invoice and dealer_margin_pct to prevent target leakage) on a
stratified 80/20 split. Writes reports/metrics.json with 95% bootstrap CIs and renders
monochrome/emerald charts in img/.
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
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "CarsDataset.csv"
REPORTS_DIR = PROJECT_DIR / "reports"
IMG_DIR = PROJECT_DIR / "img"

NUMERIC_FEATURES = [
    "EngineSize",
    "Cylinders",
    "Horsepower",
    "MPG_City",
    "MPG_Highway",
    "Weight",
    "Wheelbase",
    "Length",
    "power_to_weight",
    "mpg_combined",
]

CATEGORICAL_FEATURES = [
    "Type",
    "Origin",
    "DriveTrain",
]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

FORBIDDEN_LEAKAGE_FEATURES = {"Invoice", "dealer_margin_pct", "MSRP"}


def parse_currency(series: pd.Series) -> pd.Series:
    """Strip '$', ',', and whitespace and convert to float."""
    return (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .astype(float)
    )


def load_and_clean_data(csv_path: Path = DATA_PATH) -> pd.DataFrame:
    """Load CarsDataset.csv, parse currency columns, impute Cylinders, and engineer features."""
    df = pd.read_csv(csv_path).copy()
    for col in ["Make", "Model", "Type", "Origin", "DriveTrain"]:
        df[col] = df[col].astype(str).str.strip()

    df["MSRP_num"] = parse_currency(df["MSRP"])
    df["Invoice_num"] = parse_currency(df["Invoice"])

    # Impute missing Cylinders (e.g. Mazda RX-8 rotary engine) with median cylinders (4.0 for <2.0L)
    missing_cyl_mask = df["Cylinders"].isna()
    df.loc[missing_cyl_mask, "Cylinders"] = 4.0

    # Engineer domain automotive features
    df["power_to_weight"] = (df["Horsepower"].astype(float) / df["Weight"].astype(float)) * 1000.0
    df["mpg_combined"] = 0.55 * df["MPG_City"].astype(float) + 0.45 * df["MPG_Highway"].astype(float)
    df["dealer_margin_pct"] = (
        (df["MSRP_num"] - df["Invoice_num"]) / df["MSRP_num"]
    ) * 100.0

    return df


def bootstrap_pricing_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_boot: int = 500,
    seed: int = 42,
) -> dict[str, Any]:
    """Compute MAE, RMSE, MAPE, and R2 point estimates and 95% bootstrap CIs."""
    rng = np.random.default_rng(seed)
    n = len(y_true)

    point = {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mape": float(mean_absolute_percentage_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }

    samples: dict[str, list[float]] = {k: [] for k in point}
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        yt = y_true[idx]
        yp = y_pred[idx]
        samples["mae"].append(float(mean_absolute_error(yt, yp)))
        samples["rmse"].append(float(np.sqrt(mean_squared_error(yt, yp))))
        samples["mape"].append(float(mean_absolute_percentage_error(yt, yp)))
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
    y_test: np.ndarray,
    pred_ridge: np.ndarray,
    pred_gbr: np.ndarray,
    fi_df: pd.DataFrame,
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

    max_msrp = float(max(np.max(y_test), np.max(pred_gbr))) * 1.05
    ax1.scatter(
        y_test / 1000.0,
        pred_ridge / 1000.0,
        color="#52525B",
        alpha=0.55,
        s=32,
        label="Log-Ridge Baseline",
    )
    ax1.scatter(
        y_test / 1000.0,
        pred_gbr / 1000.0,
        color="#10B981",
        alpha=0.80,
        s=38,
        label="Gradient Boosting Regressor",
    )
    ax1.plot(
        [10, max_msrp / 1000.0],
        [10, max_msrp / 1000.0],
        color="#F4F4F5",
        linestyle="--",
        linewidth=1.4,
        label="Ideal 1:1 Valuation",
    )
    ax1.set_title(
        "Hedonic MSRP Valuation: Actual vs Predicted ($k USD, Test Set)",
        color="#F4F4F5",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax1.set_xlabel("Actual Manufacturer Suggested Retail Price ($k)", color="#D4D4D8", fontsize=11)
    ax1.set_ylabel("Predicted MSRP from Physical Specs ($k)", color="#D4D4D8", fontsize=11)
    ax1.legend(facecolor="#18181B", edgecolor="#2A2A2E", labelcolor="#E4E4E7", fontsize=9.5)

    top_f = fi_df.sort_values("importance_mean", ascending=True).tail(10)
    bar_colors = ["#10B981" if i >= len(top_f) - 3 else "#71717A" for i in range(len(top_f))]
    ax2.barh(
        top_f["feature"],
        top_f["importance_mean"],
        xerr=top_f["importance_std"],
        color=bar_colors,
        height=0.65,
        error_kw={"ecolor": "#D4D4D8", "elinewidth": 1.0, "capsize": 3},
    )
    ax2.set_title(
        "TopHedonic Pricing Drivers (Permutation R² Impact)",
        color="#F4F4F5",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax2.set_xlabel("Mean Decrease in R² when Permuted (Test Set)", color="#D4D4D8", fontsize=11)

    fig.suptitle(
        "Automotive Hedonic Pricing Model · Physical Specs & Origin → MSRP",
        color="#FFFFFF",
        fontsize=16,
        fontweight="bold",
        y=0.97,
    )
    fig.tight_layout(rect=[0, 0.02, 1, 0.93])
    fig.savefig(img_dir / "hero.png", dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)

    # Square image (1200x1200)
    fig_sq, ax_sq = plt.subplots(figsize=(12, 12), dpi=100, facecolor="#0B0B0C")
    ax_sq.set_facecolor("#121215")
    ax_sq.tick_params(colors="#D4D4D8", labelsize=11)
    for spine in ax_sq.spines.values():
        spine.set_color("#2A2A2E")
    ax_sq.grid(True, color="#222226", linestyle="--", linewidth=0.8, alpha=0.8)

    ax_sq.scatter(
        y_test / 1000.0,
        pred_gbr / 1000.0,
        color="#10B981",
        alpha=0.85,
        s=50,
        label="Gradient Boosting (Test Split)",
    )
    ax_sq.plot([10, max_msrp / 1000.0], [10, max_msrp / 1000.0], color="#F4F4F5", linestyle="--")
    ax_sq.set_title(
        "Hedonic Vehicle Pricing Accuracy ($k USD, Out-of-Sample)",
        color="#FFFFFF",
        fontsize=15,
        fontweight="bold",
        pad=15,
    )
    ax_sq.set_xlabel("Actual MSRP ($k USD)", color="#D4D4D8", fontsize=12)
    ax_sq.set_ylabel("Predicted MSRP ($k USD)", color="#D4D4D8", fontsize=12)
    ax_sq.legend(facecolor="#18181B", edgecolor="#2A2A2E", labelcolor="#E4E4E7", fontsize=11)
    fig_sq.tight_layout()
    fig_sq.savefig(img_dir / "post_square.png", dpi=100, facecolor=fig_sq.get_facecolor())
    plt.close(fig_sq)


def run_pipeline(seed: int = 42) -> dict[str, Any]:
    """Execute automotive hedonic pricing pipeline and write reports/metrics.json."""
    raw_df = pd.read_csv(DATA_PATH)
    n_missing_cyl = int(raw_df["Cylinders"].isna().sum())

    df = load_and_clean_data(DATA_PATH)
    X = df[ALL_FEATURES].copy()
    y = df["MSRP_num"].to_numpy(dtype=float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=df["Origin"], random_state=seed
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ]
    )

    # Train models in log-MSRP space to stabilize right-skewed luxury vehicle variance
    y_train_log = np.log(y_train)

    ridge_pipe = Pipeline(
        [("prep", preprocessor), ("reg", Ridge(alpha=5.0, random_state=seed))]
    )
    ridge_pipe.fit(X_train, y_train_log)
    pred_ridge = np.exp(ridge_pipe.predict(X_test))

    gbr_pipe = Pipeline(
        [
            ("prep", preprocessor),
            (
                "reg",
                GradientBoostingRegressor(
                    n_estimators=250,
                    learning_rate=0.05,
                    max_depth=3,
                    min_samples_leaf=5,
                    subsample=0.85,
                    random_state=seed,
                ),
            ),
        ]
    )
    gbr_pipe.fit(X_train, y_train_log)
    pred_gbr = np.exp(gbr_pipe.predict(X_test))

    ridge_metrics = bootstrap_pricing_metrics(y_test, pred_ridge, n_boot=500, seed=seed)
    gbr_metrics = bootstrap_pricing_metrics(y_test, pred_gbr, n_boot=500, seed=seed)

    perm = permutation_importance(
        gbr_pipe, X_test, np.log(y_test), scoring="r2", n_repeats=15, random_state=seed
    )
    fi_df = pd.DataFrame(
        {
            "feature": ALL_FEATURES,
            "importance_mean": perm.importances_mean,
            "importance_std": perm.importances_std,
        }
    ).sort_values("importance_mean", ascending=False)

    render_charts(y_test, pred_ridge, pred_gbr, fi_df, IMG_DIR)

    origin_summary = (
        df.groupby("Origin", as_index=False)
        .agg(
            vehicles=("Model", "count"),
            median_msrp_usd=("MSRP_num", lambda s: round(float(np.median(s)), 2)),
            mean_msrp_usd=("MSRP_num", lambda s: round(float(np.mean(s)), 2)),
            mean_dealer_margin_pct=("dealer_margin_pct", lambda s: round(float(np.mean(s)), 2)),
            mean_horsepower=("Horsepower", lambda s: round(float(np.mean(s)), 1)),
            mean_mpg_combined=("mpg_combined", lambda s: round(float(np.mean(s)), 2)),
        )
        .sort_values("median_msrp_usd", ascending=False)
        .to_dict(orient="records")
    )

    type_summary = (
        df.groupby("Type", as_index=False)
        .agg(
            vehicles=("Model", "count"),
            median_msrp_usd=("MSRP_num", lambda s: round(float(np.median(s)), 2)),
            mean_dealer_margin_pct=("dealer_margin_pct", lambda s: round(float(np.mean(s)), 2)),
            mean_mpg_combined=("mpg_combined", lambda s: round(float(np.mean(s)), 2)),
        )
        .sort_values("median_msrp_usd", ascending=False)
        .to_dict(orient="records")
    )

    report = {
        "dataset": {
            "total_vehicles": len(df),
            "missing_cylinders_imputed": n_missing_cyl,
            "train_vehicles": len(X_train),
            "test_vehicles": len(X_test),
            "mean_msrp_usd": round(float(df["MSRP_num"].mean()), 2),
            "median_msrp_usd": round(float(df["MSRP_num"].median()), 2),
            "mean_dealer_margin_pct": round(float(df["dealer_margin_pct"].mean()), 2),
            "mean_mpg_combined": round(float(df["mpg_combined"].mean()), 2),
        },
        "features_used": ALL_FEATURES,
        "models": {
            "log_ridge_baseline": ridge_metrics,
            "gradient_boosting_regressor": gbr_metrics,
        },
        "top_features": [
            {
                "feature": row["feature"],
                "importance_mean": round(float(row["importance_mean"]), 4),
                "importance_std": round(float(row["importance_std"]), 4),
            }
            for _, row in fi_df.head(8).iterrows()
        ],
        "origin_segments": origin_summary,
        "vehicle_type_segments": type_summary,
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    results = run_pipeline()
    print(json.dumps(results, indent=2))
