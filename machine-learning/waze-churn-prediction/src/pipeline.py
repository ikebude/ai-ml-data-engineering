"""
Waze User Churn Prediction Pipeline.

Loads waze_dataset.csv, drops rows with missing labels, engineers behavioural ratios
(km_per_drive, km_per_driving_day, drives_per_driving_day, pct_sessions_fav, device_encoded),
evaluates a Logistic Regression baseline against an Isotonic-Calibrated HistGradientBoosting
and RandomForest classifier on a stratified 80/20 split, computes PR-AUC, ROC-AUC,
Recall @ 10% and 20% contact rates with 95% bootstrap confidence intervals, saves
reports/metrics.json, and renders monochrome/emerald charts in img/.
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
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "waze_dataset.csv"
REPORTS_DIR = PROJECT_DIR / "reports"
IMG_DIR = PROJECT_DIR / "img"

FEATURE_COLS = [
    "sessions",
    "drives",
    "total_sessions",
    "n_days_after_onboarding",
    "total_navigations_fav1",
    "total_navigations_fav2",
    "driven_km_drives",
    "duration_minutes_drives",
    "activity_days",
    "driving_days",
    "km_per_drive",
    "km_per_driving_day",
    "drives_per_driving_day",
    "pct_sessions_fav",
    "device_encoded",
]


def load_and_clean_data(csv_path: Path = DATA_PATH) -> pd.DataFrame:
    """Load Waze dataset and drop rows with missing churn label."""
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["label"]).copy()
    df["target"] = (df["label"].str.strip().str.lower() == "churned").astype(int)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer domain behavioural features without target leakage."""
    out = df.copy()
    out["km_per_drive"] = np.where(
        out["drives"] > 0, out["driven_km_drives"] / out["drives"], 0.0
    )
    out["km_per_driving_day"] = np.where(
        out["driving_days"] > 0, out["driven_km_drives"] / out["driving_days"], 0.0
    )
    out["drives_per_driving_day"] = np.where(
        out["driving_days"] > 0, out["drives"] / out["driving_days"], 0.0
    )
    total_fav = out["total_navigations_fav1"] + out["total_navigations_fav2"]
    out["pct_sessions_fav"] = np.where(
        out["total_sessions"] > 0, total_fav / out["total_sessions"], 0.0
    )
    out["device_encoded"] = (out["device"].str.strip().str.lower() == "iphone").astype(int)

    # Cap any extreme infinities if present
    for col in ["km_per_drive", "km_per_driving_day", "drives_per_driving_day", "pct_sessions_fav"]:
        out[col] = np.nan_to_num(out[col], nan=0.0, posinf=0.0, neginf=0.0)
    return out


def recall_at_k(y_true: np.ndarray, y_score: np.ndarray, k_fraction: float) -> float:
    """Compute recall of positive class when contacting top k_fraction of scored users."""
    n = len(y_true)
    top_k = max(1, int(np.floor(n * k_fraction)))
    order = np.argsort(y_score)[::-1][:top_k]
    total_pos = np.sum(y_true)
    if total_pos == 0:
        return 0.0
    return float(np.sum(y_true[order]) / total_pos)


def precision_at_k(y_true: np.ndarray, y_score: np.ndarray, k_fraction: float) -> float:
    """Compute precision in the top k_fraction of scored users."""
    n = len(y_true)
    top_k = max(1, int(np.floor(n * k_fraction)))
    order = np.argsort(y_score)[::-1][:top_k]
    return float(np.mean(y_true[order]))


def bootstrap_metrics(
    y_true: np.ndarray,
    y_score: np.ndarray,
    n_boot: int = 500,
    seed: int = 42,
) -> dict[str, Any]:
    """Compute point estimates and 95% bootstrap CIs for churn ranking metrics."""
    rng = np.random.default_rng(seed)
    n = len(y_true)

    point = {
        "pr_auc": float(average_precision_score(y_true, y_score)),
        "roc_auc": float(roc_auc_score(y_true, y_score)),
        "brier_score": float(brier_score_loss(y_true, y_score)),
        "recall_at_10pct": recall_at_k(y_true, y_score, 0.10),
        "recall_at_20pct": recall_at_k(y_true, y_score, 0.20),
        "precision_at_10pct": precision_at_k(y_true, y_score, 0.10),
        "precision_at_20pct": precision_at_k(y_true, y_score, 0.20),
    }

    samples: dict[str, list[float]] = {k: [] for k in point}
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        yb = y_true[idx]
        sb = y_score[idx]
        if len(np.unique(yb)) < 2:
            continue
        samples["pr_auc"].append(float(average_precision_score(yb, sb)))
        samples["roc_auc"].append(float(roc_auc_score(yb, sb)))
        samples["brier_score"].append(float(brier_score_loss(yb, sb)))
        samples["recall_at_10pct"].append(recall_at_k(yb, sb, 0.10))
        samples["recall_at_20pct"].append(recall_at_k(yb, sb, 0.20))
        samples["precision_at_10pct"].append(precision_at_k(yb, sb, 0.10))
        samples["precision_at_20pct"].append(precision_at_k(yb, sb, 0.20))

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
    scores_dict: dict[str, np.ndarray],
    feature_importance_df: pd.DataFrame,
    base_rate: float,
    img_dir: Path = IMG_DIR,
) -> None:
    """Render monochrome + emerald portfolio figures (hero 1600x900 and square 1200x1200)."""
    img_dir.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "axes.edgecolor": "#2A2A2E",
            "axes.linewidth": 0.9,
        }
    )

    # 1. Hero chart (1600x900 @ 100 dpi -> 16x9 in)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9), dpi=100, facecolor="#0B0B0C")
    for ax in (ax1, ax2):
        ax.set_facecolor("#121215")
        ax.tick_params(colors="#D4D4D8", labelsize=10)
        for spine in ax.spines.values():
            spine.set_color("#2A2A2E")
        ax.grid(True, color="#222226", linestyle="--", linewidth=0.7, alpha=0.8)

    # Left panel: Precision-Recall Curve
    colors = {
        "Calibrated HistGradientBoosting": "#10B981",  # Emerald
        "Calibrated RandomForest": "#A1A1AA",          # Light Zinc
        "Logistic Regression Baseline": "#52525B",     # Muted Zinc
    }
    linewidths = {
        "Calibrated HistGradientBoosting": 2.6,
        "Calibrated RandomForest": 1.8,
        "Logistic Regression Baseline": 1.8,
    }
    for name, probs in scores_dict.items():
        prec, rec, _ = precision_recall_curve(y_test, probs)
        ap = average_precision_score(y_test, probs)
        ax1.plot(
            rec,
            prec,
            label=f"{name} (PR-AUC = {ap:.3f})",
            color=colors.get(name, "#A1A1AA"),
            linewidth=linewidths.get(name, 2.0),
        )

    ax1.axhline(
        base_rate,
        color="#EF4444",
        linestyle=":",
        linewidth=1.4,
        label=f"Random Baseline ({base_rate:.3f})",
    )
    ax1.set_title(
        "Precision-Recall Curve (Out-of-Sample Test Split)",
        color="#F4F4F5",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax1.set_xlabel("Recall (Fraction of Churned Users Captured)", color="#D4D4D8", fontsize=11)
    ax1.set_ylabel("Precision (Churn Rate in Contact Cohort)", color="#D4D4D8", fontsize=11)
    ax1.legend(facecolor="#18181B", edgecolor="#2A2A2E", labelcolor="#E4E4E7", fontsize=9.5)

    # Right panel: Top Permutation Feature Importances
    top_f = feature_importance_df.sort_values("importance_mean", ascending=True).tail(10)
    bar_colors = ["#10B981" if i >= len(top_f) - 3 else "#71717A" for i in range(len(top_f))]
    ax2.barh(
        top_f["feature"],
        top_f["importance_mean"],
        xerr=top_f["importance_std"],
        color=bar_colors,
        edgecolor="none",
        height=0.65,
        error_kw={"ecolor": "#D4D4D8", "elinewidth": 1.0, "capsize": 3},
    )
    ax2.set_title(
        "Top 10 Churn Predictors (Permutation PR-AUC Drop)",
        color="#F4F4F5",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax2.set_xlabel("Mean Decrease in PR-AUC (Test Set)", color="#D4D4D8", fontsize=11)

    fig.suptitle(
        "Waze User Churn Prediction · Calibrated Gradient Boosting vs Baseline",
        color="#FFFFFF",
        fontsize=16,
        fontweight="bold",
        y=0.97,
    )
    fig.tight_layout(rect=[0, 0.02, 1, 0.93])
    fig.savefig(img_dir / "hero.png", dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)

    # 2. Square Social Post chart (1200x1200 @ 100 dpi -> 12x12 in)
    fig_sq, ax_sq = plt.subplots(figsize=(12, 12), dpi=100, facecolor="#0B0B0C")
    ax_sq.set_facecolor("#121215")
    ax_sq.tick_params(colors="#D4D4D8", labelsize=11)
    for spine in ax_sq.spines.values():
        spine.set_color("#2A2A2E")
    ax_sq.grid(True, color="#222226", linestyle="--", linewidth=0.8, alpha=0.8)

    contact_rates = np.linspace(0.05, 0.50, 10)
    for name, probs in scores_dict.items():
        recalls = [recall_at_k(y_test, probs, r) for r in contact_rates]
        ax_sq.plot(
            contact_rates * 100,
            np.array(recalls) * 100,
            marker="o",
            label=name,
            color=colors.get(name, "#A1A1AA"),
            linewidth=linewidths.get(name, 2.0),
        )
    ax_sq.plot(
        contact_rates * 100,
        contact_rates * 100,
        linestyle=":",
        color="#EF4444",
        linewidth=1.5,
        label="Random Targeting",
    )
    ax_sq.set_title(
        "Cumulative Churn Recall by Retention Contact Budget (%)",
        color="#FFFFFF",
        fontsize=15,
        fontweight="bold",
        pad=15,
    )
    ax_sq.set_xlabel("Users Contacted (% of Active Base)", color="#D4D4D8", fontsize=12)
    ax_sq.set_ylabel("Churned Users Captured (% Recall)", color="#D4D4D8", fontsize=12)
    ax_sq.legend(facecolor="#18181B", edgecolor="#2A2A2E", labelcolor="#E4E4E7", fontsize=11)
    fig_sq.tight_layout()
    fig_sq.savefig(img_dir / "post_square.png", dpi=100, facecolor=fig_sq.get_facecolor())
    plt.close(fig_sq)


def run_pipeline(seed: int = 42) -> dict[str, Any]:
    """Execute end-to-end Waze churn pipeline and write reports/metrics.json."""
    raw_df = pd.read_csv(DATA_PATH)
    n_raw = len(raw_df)
    n_missing_label = int(raw_df["label"].isna().sum())

    clean_df = load_and_clean_data(DATA_PATH)
    feat_df = engineer_features(clean_df)

    X = feat_df[FEATURE_COLS].to_numpy(dtype=float)
    y = feat_df["target"].to_numpy(dtype=int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=seed
    )

    # 1. Baseline: Logistic Regression with StandardScaler
    lr_pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=seed)),
        ]
    )
    lr_pipe.fit(X_train, y_train)
    lr_probs = lr_pipe.predict_proba(X_test)[:, 1]

    # 2. Random Forest with Isotonic Calibration
    rf_base = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=20,
        random_state=seed,
        n_jobs=-1,
    )
    rf_cal = CalibratedClassifierCV(estimator=rf_base, method="isotonic", cv=5)
    rf_cal.fit(X_train, y_train)
    rf_probs = rf_cal.predict_proba(X_test)[:, 1]

    # 3. HistGradientBoosting with Isotonic Calibration
    hgb_base = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.05,
        max_leaf_nodes=15,
        min_samples_leaf=30,
        l2_regularization=1.0,
        random_state=seed,
    )
    hgb_cal = CalibratedClassifierCV(estimator=hgb_base, method="isotonic", cv=5)
    hgb_cal.fit(X_train, y_train)
    hgb_probs = hgb_cal.predict_proba(X_test)[:, 1]

    lr_metrics = bootstrap_metrics(y_test, lr_probs, n_boot=500, seed=seed)
    rf_metrics = bootstrap_metrics(y_test, rf_probs, n_boot=500, seed=seed)
    hgb_metrics = bootstrap_metrics(y_test, hgb_probs, n_boot=500, seed=seed)

    # Permutation importance on the best tree model (or Logistic Regression if close)
    perm = permutation_importance(
        hgb_cal,
        X_test,
        y_test,
        scoring="average_precision",
        n_repeats=10,
        random_state=seed,
        n_jobs=-1,
    )
    fi_df = pd.DataFrame(
        {
            "feature": FEATURE_COLS,
            "importance_mean": perm.importances_mean,
            "importance_std": perm.importances_std,
        }
    ).sort_values("importance_mean", ascending=False)

    scores_dict = {
        "Calibrated HistGradientBoosting": hgb_probs,
        "Calibrated RandomForest": rf_probs,
        "Logistic Regression Baseline": lr_probs,
    }
    base_rate = float(np.mean(y_test))
    render_charts(y_test, scores_dict, fi_df, base_rate, IMG_DIR)

    # Behavioural cohort insights from full cleaned dataset
    churned_mask = feat_df["target"] == 1
    retained_mask = feat_df["target"] == 0
    cohort_summary = {
        "median_driving_days_churned": float(feat_df.loc[churned_mask, "driving_days"].median()),
        "median_driving_days_retained": float(feat_df.loc[retained_mask, "driving_days"].median()),
        "median_km_per_driving_day_churned": round(
            float(feat_df.loc[churned_mask, "km_per_driving_day"].median()), 2
        ),
        "median_km_per_driving_day_retained": round(
            float(feat_df.loc[retained_mask, "km_per_driving_day"].median()), 2
        ),
        "median_onboarding_days_churned": float(
            feat_df.loc[churned_mask, "n_days_after_onboarding"].median()
        ),
        "median_onboarding_days_retained": float(
            feat_df.loc[retained_mask, "n_days_after_onboarding"].median()
        ),
        "churn_rate_iphone": round(
            float(feat_df.loc[feat_df["device_encoded"] == 1, "target"].mean()), 4
        ),
        "churn_rate_android": round(
            float(feat_df.loc[feat_df["device_encoded"] == 0, "target"].mean()), 4
        ),
    }

    report = {
        "dataset": {
            "total_rows": n_raw,
            "missing_label_dropped": n_missing_label,
            "clean_rows": len(feat_df),
            "train_rows": len(y_train),
            "test_rows": len(y_test),
            "churn_rate": round(float(np.mean(y)), 4),
            "test_churn_rate": round(base_rate, 4),
        },
        "models": {
            "logistic_regression_baseline": lr_metrics,
            "calibrated_random_forest": rf_metrics,
            "calibrated_hist_gradient_boosting": hgb_metrics,
        },
        "top_features": [
            {
                "feature": row["feature"],
                "importance_mean": round(float(row["importance_mean"]), 4),
                "importance_std": round(float(row["importance_std"]), 4),
            }
            for _, row in fi_df.head(8).iterrows()
        ],
        "cohort_insights": cohort_summary,
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    results = run_pipeline()
    print(json.dumps(results, indent=2))
