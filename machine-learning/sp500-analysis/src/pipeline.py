"""
S&P 500 Financial Factor Clustering, Anomaly Detection & Tier Classification Pipeline.

Loads sp500_companies.csv (502 companies), imputes missing fundamentals by GICS sector
median, engineers financial ratios (log_marketcap, ebitda_margin_proxy, price_to_ebitda,
revenue_growth, employees_per_bn_mcap), performs robust MAD Z-score anomaly detection,
applies StandardScaler + PCA + K-Means clustering (selecting optimal k via silhouette
score), evaluates a Random Forest vs Logistic Regression benchmark for market-cap tier
and GICS sector classification, writes reports/metrics.json, and renders monochrome/emerald
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
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, silhouette_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "sp500_companies.csv"
REPORTS_DIR = PROJECT_DIR / "reports"
IMG_DIR = PROJECT_DIR / "img"

CLUSTER_FEATURES = [
    "log_marketcap",
    "ebitda_margin_proxy",
    "price_to_ebitda",
    "revenue_growth",
    "employees_per_bn_mcap",
    "Currentprice",
]


def load_and_engineer_features(csv_path: Path = DATA_PATH) -> pd.DataFrame:
    """Load S&P 500 dataset, impute missing values by sector median, and engineer ratios."""
    df = pd.read_csv(csv_path).copy()

    # Impute Ebitda, Revenuegrowth, Fulltimeemployees by Sector median then global median
    for col in ["Ebitda", "Revenuegrowth", "Fulltimeemployees"]:
        sector_med = df.groupby("Sector")[col].transform("median")
        df[col] = df[col].fillna(sector_med).fillna(df[col].median())

    df["log_marketcap"] = np.log10(np.maximum(df["Marketcap"].astype(float), 1.0))
    # EBITDA-to-MarketCap yield proxy (bounded for extreme outliers)
    df["ebitda_margin_proxy"] = np.clip(
        df["Ebitda"].astype(float) / np.maximum(df["Marketcap"].astype(float), 1.0),
        -0.5,
        0.5,
    )
    # Enterprise valuation multiple proxy: Marketcap / max(Ebitda, 1e7) capped at [0, 150]
    raw_p_ebitda = np.where(
        df["Ebitda"] > 0,
        df["Marketcap"].astype(float) / df["Ebitda"].astype(float),
        100.0,
    )
    df["price_to_ebitda"] = np.clip(raw_p_ebitda, 1.0, 150.0)
    df["revenue_growth"] = np.clip(df["Revenuegrowth"].astype(float), -0.8, 3.0)
    df["employees_per_bn_mcap"] = np.clip(
        df["Fulltimeemployees"].astype(float) / (df["Marketcap"].astype(float) / 1e9),
        0.1,
        5000.0,
    )

    # Market-cap tier target for supervised classification benchmark (Mega/Large/Mid)
    df["mcap_tier"] = pd.qcut(
        df["Marketcap"], q=3, labels=["Mid-Cap S&P", "Large-Cap S&P", "Mega-Cap S&P"]
    ).astype(str)

    return df


def detect_robust_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Compute multivariate robust MAD Z-score across financial ratios."""
    out = df.copy()
    z_matrix = []
    for col in CLUSTER_FEATURES:
        vals = out[col].to_numpy(dtype=float)
        med = np.median(vals)
        mad = np.median(np.abs(vals - med))
        scale = 1.4826 * mad if mad > 1e-9 else np.std(vals)
        z_matrix.append(np.abs(vals - med) / max(scale, 1e-9))

    z_arr = np.vstack(z_matrix).T
    out["robust_z_max"] = np.max(z_arr, axis=1)
    out["robust_z_mean"] = np.mean(z_arr, axis=1)
    out["is_outlier"] = (out["robust_z_max"] > 3.5).astype(int)
    return out


def fit_pca_and_kmeans(
    df: pd.DataFrame, k_candidates: tuple[int, ...] = (3, 4, 5, 6), seed: int = 42
) -> tuple[pd.DataFrame, dict[str, Any], np.ndarray]:
    """Scale features, fit 2D PCA, and select optimal K-Means cluster count via Silhouette."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[CLUSTER_FEATURES].to_numpy(dtype=float))

    pca = PCA(n_components=3, random_state=seed)
    X_pca = pca.fit_transform(X_scaled)

    sil_scores: dict[int, float] = {}
    models: dict[int, KMeans] = {}
    for k in k_candidates:
        km = KMeans(n_clusters=k, n_init=20, random_state=seed)
        labels = km.fit_predict(X_scaled)
        sil_scores[k] = float(silhouette_score(X_scaled, labels))
        models[k] = km

    best_k = max(sil_scores, key=sil_scores.get)
    best_km = models[best_k]
    out = df.copy()
    out["cluster"] = best_km.labels_
    out["pca_1"] = X_pca[:, 0]
    out["pca_2"] = X_pca[:, 1]
    out["pca_3"] = X_pca[:, 2]

    pca_meta = {
        "optimal_k": int(best_k),
        "silhouette_score": round(sil_scores[best_k], 4),
        "silhouette_by_k": {str(k): round(v, 4) for k, v in sil_scores.items()},
        "pca_explained_variance_ratio": [
            round(float(v), 4) for v in pca.explained_variance_ratio_
        ],
        "pca_2d_cumulative_variance": round(
            float(np.sum(pca.explained_variance_ratio_[:2])), 4
        ),
        "pca_3d_cumulative_variance": round(
            float(np.sum(pca.explained_variance_ratio_[:3])), 4
        ),
    }
    return out, pca_meta, X_scaled


def evaluate_classification_benchmark(df: pd.DataFrame, seed: int = 42) -> dict[str, Any]:
    """Benchmark Random Forest vs Logistic Regression on fundamental factor features (no Marketcap)."""
    # Predict mcap_tier from operational/fundamental ratios excluding log_marketcap and Weight
    fundamental_cols = [
        "Ebitda",
        "Revenuegrowth",
        "Fulltimeemployees",
        "Currentprice",
        "price_to_ebitda",
    ]
    X = df[fundamental_cols].to_numpy(dtype=float)
    y = df["mcap_tier"].to_numpy()

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)

    lr_pipe = Pipeline(
        [("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=1000, random_state=seed))]
    )
    rf_clf = RandomForestClassifier(
        n_estimators=300, max_depth=8, min_samples_leaf=5, random_state=seed, n_jobs=-1
    )

    y_pred_lr = cross_val_predict(lr_pipe, X, y, cv=skf)
    y_pred_rf = cross_val_predict(rf_clf, X, y, cv=skf)

    # Bootstrap 95% CIs on OOF predictions
    rng = np.random.default_rng(seed)
    n = len(y)
    rf_f1_boot, lr_f1_boot = [], []
    for _ in range(500):
        idx = rng.integers(0, n, size=n)
        rf_f1_boot.append(float(f1_score(y[idx], y_pred_rf[idx], average="macro")))
        lr_f1_boot.append(float(f1_score(y[idx], y_pred_lr[idx], average="macro")))

    return {
        "target": "mcap_tier (3-class stratified 5-fold CV from operational fundamentals)",
        "features_used": fundamental_cols,
        "logistic_regression_baseline": {
            "accuracy": round(float(accuracy_score(y, y_pred_lr)), 4),
            "macro_f1": round(float(f1_score(y, y_pred_lr, average="macro")), 4),
            "macro_f1_ci_95": [
                round(float(np.percentile(lr_f1_boot, 2.5)), 4),
                round(float(np.percentile(lr_f1_boot, 97.5)), 4),
            ],
        },
        "random_forest_classifier": {
            "accuracy": round(float(accuracy_score(y, y_pred_rf)), 4),
            "macro_f1": round(float(f1_score(y, y_pred_rf, average="macro")), 4),
            "macro_f1_ci_95": [
                round(float(np.percentile(rf_f1_boot, 2.5)), 4),
                round(float(np.percentile(rf_f1_boot, 97.5)), 4),
            ],
        },
    }


def render_charts(df: pd.DataFrame, pca_meta: dict[str, Any], img_dir: Path = IMG_DIR) -> None:
    """Render monochrome + emerald portfolio figures (1600x900 hero and 1200x1200 square)."""
    img_dir.mkdir(parents=True, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9), dpi=100, facecolor="#0B0B0C")
    for ax in (ax1, ax2):
        ax.set_facecolor("#121215")
        ax.tick_params(colors="#D4D4D8", labelsize=10)
        for spine in ax.spines.values():
            spine.set_color("#2A2A2E")
        ax.grid(True, color="#222226", linestyle="--", linewidth=0.7, alpha=0.8)

    palette = ["#10B981", "#A1A1AA", "#52525B", "#F59E0B", "#3B82F6", "#EC4899"]
    for cid in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == cid]
        ax1.scatter(
            sub["pca_1"],
            sub["pca_2"],
            s=36,
            alpha=0.8,
            color=palette[cid % len(palette)],
            label=f"Cluster {cid} (n={len(sub)})",
        )

    # Annotate top 6 market-cap/outlier tickers
    top_tickers = df.sort_values("Marketcap", ascending=False).head(6)
    for _, row in top_tickers.iterrows():
        ax1.annotate(
            row["Symbol"],
            (row["pca_1"], row["pca_2"]),
            xytext=(6, 4),
            textcoords="offset points",
            color="#FFFFFF",
            fontsize=9,
            fontweight="bold",
        )

    v1 = pca_meta["pca_explained_variance_ratio"][0] * 100
    v2 = pca_meta["pca_explained_variance_ratio"][1] * 100
    ax1.set_title(
        f"PCA Factor Projection & K-Means Regimes (k={pca_meta['optimal_k']}, Sil={pca_meta['silhouette_score']:.3f})",
        color="#F4F4F5",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax1.set_xlabel(f"Principal Component 1 ({v1:.1f}% Variance)", color="#D4D4D8", fontsize=11)
    ax1.set_ylabel(f"Principal Component 2 ({v2:.1f}% Variance)", color="#D4D4D8", fontsize=11)
    ax1.legend(facecolor="#18181B", edgecolor="#2A2A2E", labelcolor="#E4E4E7", fontsize=9.5)

    # Right panel: Sector Market Cap Concentration ($ Trillions)
    sec_df = (
        df.groupby("Sector", as_index=False)
        .agg(total_mcap_tn=("Marketcap", lambda s: np.sum(s) / 1e12), count=("Symbol", "count"))
        .sort_values("total_mcap_tn", ascending=True)
    )
    bar_colors = ["#10B981" if i >= len(sec_df) - 3 else "#71717A" for i in range(len(sec_df))]
    ax2.barh(sec_df["Sector"], sec_df["total_mcap_tn"], color=bar_colors, height=0.65)
    ax2.set_title(
        "S&P 500 Market Capitalization by GICS Sector ($ Trillions)",
        color="#F4F4F5",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax2.set_xlabel("Aggregate Market Cap ($ Trillions USD)", color="#D4D4D8", fontsize=11)

    fig.suptitle(
        "S&P 500 Quantitative Factor Clustering & Sector Concentration Analysis",
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

    ax_sq.barh(sec_df["Sector"], sec_df["total_mcap_tn"], color=bar_colors, height=0.65)
    ax_sq.set_title(
        "S&P 500 Capital Concentration Across 11 GICS Sectors ($T)",
        color="#FFFFFF",
        fontsize=15,
        fontweight="bold",
        pad=15,
    )
    ax_sq.set_xlabel("Aggregate Market Cap ($ Trillions USD)", color="#D4D4D8", fontsize=12)
    fig_sq.tight_layout()
    fig_sq.savefig(img_dir / "post_square.png", dpi=100, facecolor=fig_sq.get_facecolor())
    plt.close(fig_sq)


def run_pipeline(seed: int = 42) -> dict[str, Any]:
    """Execute S&P 500 analysis pipeline and write reports/metrics.json."""
    df = load_and_engineer_features(DATA_PATH)
    df = detect_robust_outliers(df)
    df, pca_meta, _ = fit_pca_and_kmeans(df, seed=seed)
    clf_bench = evaluate_classification_benchmark(df, seed=seed)

    render_charts(df, pca_meta, IMG_DIR)

    total_mcap = float(df["Marketcap"].sum())
    top10_mcap = float(df.sort_values("Marketcap", ascending=False).head(10)["Marketcap"].sum())

    sec_summary = (
        df.groupby("Sector", as_index=False)
        .agg(
            companies=("Symbol", "count"),
            marketcap_tn=("Marketcap", lambda s: round(float(np.sum(s) / 1e12), 3)),
            weight_share=("Marketcap", lambda s: round(float(np.sum(s) / total_mcap), 4)),
            median_rev_growth=("revenue_growth", lambda s: round(float(np.median(s)), 4)),
        )
        .sort_values("marketcap_tn", ascending=False)
    )

    outliers = (
        # Several tickers tie at the same robust Z; break ties by Symbol so the top 10 does not
        # depend on numpy's CPU-specific (AVX-512 vs AVX2) unstable sort.
        df.sort_values(["robust_z_max", "Symbol"], ascending=[False, True], kind="mergesort")
        .head(10)[["Symbol", "Shortname", "Sector", "Marketcap", "robust_z_max"]]
        .to_dict(orient="records")
    )
    for o in outliers:
        o["robust_z_max"] = round(float(o["robust_z_max"]), 2)
        o["marketcap_bn"] = round(float(o.pop("Marketcap") / 1e9), 2)

    cluster_profiles = (
        df.groupby("cluster", as_index=False)
        .agg(
            count=("Symbol", "count"),
            median_mcap_bn=("Marketcap", lambda s: round(float(np.median(s) / 1e9), 2)),
            median_price_to_ebitda=("price_to_ebitda", lambda s: round(float(np.median(s)), 2)),
            median_rev_growth=("revenue_growth", lambda s: round(float(np.median(s)), 4)),
        )
        .to_dict(orient="records")
    )

    report = {
        "dataset": {
            "total_companies": len(df),
            "sectors_count": int(df["Sector"].nunique()),
            "total_marketcap_trillions_usd": round(total_mcap / 1e12, 2),
            "top_10_companies_mcap_share": round(top10_mcap / total_mcap, 4),
            "outliers_flagged_z_gt_3_5": int(df["is_outlier"].sum()),
        },
        "pca_and_clustering": pca_meta,
        "cluster_profiles": cluster_profiles,
        "classification_benchmark": clf_bench,
        "top_10_outliers": outliers,
        "sector_concentration": sec_summary.to_dict(orient="records"),
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    results = run_pipeline()
    print(json.dumps(results, indent=2))
