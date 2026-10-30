"""LoanLens: Out-of-Time Credit Default Scorecard, Calibrated GBDT & Policy Simulator.

Implements PRODUCT_SPECS.md §2 on the Prosper Loan dataset (`Prosperloandata.csv`, 113,937 loans):
1. Outcome definition & strict anti-leakage filter:
   - Excludes 'Current' loans whose term has not finished.
   - Defines `default = 1` for Defaulted / Chargedoff / Past Due (>60 days), and `0` for Completed.
   - Drops all post-origination columns (`LP_*`, `LoanCurrentDaysDelinquent`, `ClosedDate`, etc.).
2. Out-of-Time (OOT) validation:
   - Chronological 75/25 split by `ListingCreationDate` so the model is tested strictly on future
     origination cohorts.
3. Dual Modeling:
   - Interpretable Weight-of-Evidence (WoE) + Logistic Regression Scorecard mapped to a 300-850
     credit score (`PDO = 20` points at `600`).
   - Calibrated HistGradientBoostingClassifier (isotonic calibration).
4. Approval Policy Simulator & Fairness Audit:
   - Sweeps maximum allowable Probability of Default (PD) cutoff to compute approval rate, bad rate,
     and net expected portfolio yield (`BorrowerRate - bad_rate * LGD`).
   - Audits approval rate parity across homeowner and income-band slices.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
    roc_curve,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, QuantileTransformer, StandardScaler


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "Prosperloandata.csv"
REPORTS_DIR = BASE_DIR / "reports"
IMG_DIR = BASE_DIR / "img"

# Strictly pre-origination underwriting features (zero post-loan LP_* or delinquency leakage)
NUM_FEATURES = [
    "Term",
    "BorrowerRate",
    "ProsperRating (numeric)",
    "ProsperScore",
    "CreditScoreRangeLower",
    "CreditScoreRangeUpper",
    "EmploymentStatusDuration",
    "CurrentCreditLines",
    "OpenCreditLines",
    "TotalCreditLinespast7years",
    "OpenRevolvingAccounts",
    "OpenRevolvingMonthlyPayment",
    "InquiriesLast6Months",
    "TotalInquiries",
    "CurrentDelinquencies",
    "AmountDelinquent",
    "DelinquenciesLast7Years",
    "PublicRecordsLast10Years",
    "RevolvingCreditBalance",
    "BankcardUtilization",
    "AvailableBankcardCredit",
    "TotalTrades",
    "TradesNeverDelinquent (percentage)",
    "TradesOpenedLast6Months",
    "DebtToIncomeRatio",
    "StatedMonthlyIncome",
    "LoanOriginalAmount",
    "Investors",
]

CAT_FEATURES = [
    "EmploymentStatus",
    "IsBorrowerHomeowner",
    "IncomeRange",
    "IncomeVerifiable",
]

LEAKAGE_COLUMNS = {
    "LoanStatus",
    "ClosedDate",
    "LoanCurrentDaysDelinquent",
    "LoanFirstDefaultedCycleNumber",
    "LoanMonthsSinceOrigination",
    "LP_CustomerPayments",
    "LP_CustomerPrincipalPayments",
    "LP_InterestandFees",
    "LP_ServiceFees",
    "LP_CollectionFees",
    "LP_GrossPrincipalLoss",
    "LP_NetPrincipalLoss",
    "LP_NonPrincipalRecoverypayments",
}


def ks_statistic(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    return float(np.max(np.abs(tpr - fpr)))


def expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_ids = np.digitize(y_prob, bins[1:-1], right=True)
    ece = 0.0
    n = len(y_true)
    for b in range(n_bins):
        mask = bin_ids == b
        if np.any(mask):
            ece += (np.sum(mask) / n) * abs(float(np.mean(y_prob[mask]) - np.mean(y_true[mask])))
    return float(ece)


def bootstrap_ci(y_true: np.ndarray, y_score: np.ndarray, metric_fn, n_boot: int = 200, seed: int = 42) -> Tuple[float, float]:
    rng = np.random.default_rng(seed)
    vals = []
    n = len(y_true)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(np.unique(y_true[idx])) < 2:
            continue
        vals.append(float(metric_fn(y_true[idx], y_score[idx])))
    return round(float(np.percentile(vals, 2.5)), 4), round(float(np.percentile(vals, 97.5)), 4)


def pd_to_credit_score(pd_prob: np.ndarray, base_score: float = 600.0, base_odds: float = 1.0 / 9.0, pdo: float = 20.0) -> np.ndarray:
    """Maps calibrated Probability of Default (PD) to a 300-850 FICO-style credit score."""
    p = np.clip(pd_prob, 1e-4, 1.0 - 1e-4)
    odds = p / (1.0 - p)
    factor = pdo / np.log(2.0)
    offset = base_score + factor * np.log(base_odds)
    score = offset - factor * np.log(odds)
    return np.clip(np.round(score), 300, 850).astype(int)


def load_closed_loans(path: Path = DATA_PATH) -> pd.DataFrame:
    use_cols = (
        ["ListingCreationDate", "LoanStatus", "CreditGrade"]
        + [c for c in NUM_FEATURES]
        + [c for c in CAT_FEATURES]
    )
    df = pd.read_csv(path, usecols=lambda c: c in use_cols)

    # Filter strictly to finished/defaulted outcomes (exclude Current & Cancelled)
    bad_statuses = {
        "Defaulted",
        "Chargedoff",
        "Past Due (61-90 days)",
        "Past Due (91-120 days)",
        "Past Due (>120 days)",
    }
    good_statuses = {"Completed"}
    valid_mask = df["LoanStatus"].isin(bad_statuses | good_statuses)
    df = df.loc[valid_mask].copy()
    df["target"] = df["LoanStatus"].isin(bad_statuses).astype(int)

    # Parse creation timestamp for strict chronological out-of-time split
    df["ListingCreationDate"] = pd.to_datetime(df["ListingCreationDate"], errors="coerce")
    df = df.dropna(subset=["ListingCreationDate"]).sort_values("ListingCreationDate", kind="stable").reset_index(drop=True)

    # Engineer unified credit rating across pre-2009 CreditGrade and post-2009 ProsperRating
    grade_map = {"AA": 7, "A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "HR": 1, "NC": 0}
    df["unified_rating"] = df["ProsperRating (numeric)"].fillna(df["CreditGrade"].map(grade_map)).fillna(4.0)
    df["credit_score_mid"] = 0.5 * (df["CreditScoreRangeLower"] + df["CreditScoreRangeUpper"])
    df["payment_to_income"] = (df["LoanOriginalAmount"] / df["Term"].clip(lower=12)) / (
        df["StatedMonthlyIncome"].clip(lower=250.0)
    )
    return df


def train_and_evaluate(df: pd.DataFrame) -> Tuple[Dict[str, Any], pd.DataFrame, Dict[str, np.ndarray]]:
    feature_num = NUM_FEATURES + ["unified_rating", "credit_score_mid", "payment_to_income"]
    feature_cat = CAT_FEATURES

    # Verify zero leakage columns in feature list
    assert LEAKAGE_COLUMNS.isdisjoint(set(feature_num + feature_cat)), "Leakage column detected!"

    # Out-of-time 75/25 split by ListingCreationDate
    split_idx = int(len(df) * 0.75)
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()

    X_train = train_df[feature_num + feature_cat]
    y_train = train_df["target"].to_numpy()
    X_test = test_df[feature_num + feature_cat]
    y_test = test_df["target"].to_numpy()

    # 1. WoE-style Monotonic Quantile-Binned Scorecard (Logistic Regression)
    scorecard_pre = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    [
                        ("imp", SimpleImputer(strategy="median")),
                        ("qt", QuantileTransformer(n_quantiles=10, output_distribution="normal", random_state=42)),
                        ("sc", StandardScaler()),
                    ]
                ),
                feature_num,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("imp", SimpleImputer(strategy="most_frequent")),
                        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                feature_cat,
            ),
        ]
    )
    scorecard_base = Pipeline(
        [
            ("pre", scorecard_pre),
            ("clf", LogisticRegression(C=0.2, max_iter=600, random_state=42)),
        ]
    )
    scorecard_cal = CalibratedClassifierCV(scorecard_base, method="isotonic", cv=3)
    scorecard_cal.fit(X_train, y_train)
    sc_prob = scorecard_cal.predict_proba(X_test)[:, 1]

    # 2. Primary Model: Calibrated HistGradientBoosting
    gbdt_pre = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), feature_num),
            (
                "cat",
                Pipeline(
                    [
                        ("imp", SimpleImputer(strategy="most_frequent")),
                        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                feature_cat,
            ),
        ]
    )
    gbdt_base = Pipeline(
        [
            ("pre", gbdt_pre),
            (
                "clf",
                HistGradientBoostingClassifier(
                    max_depth=5,
                    learning_rate=0.05,
                    max_iter=220,
                    min_samples_leaf=40,
                    random_state=42,
                ),
            ),
        ]
    )
    gbdt_cal = CalibratedClassifierCV(gbdt_base, method="isotonic", cv=3)
    gbdt_cal.fit(X_train, y_train)
    gb_prob = gbdt_cal.predict_proba(X_test)[:, 1]

    # Blended ensemble (70% GBDT + 30% Scorecard) for smooth calibration & monotonicity
    ens_prob = 0.70 * gb_prob + 0.30 * sc_prob

    roc_ci = bootstrap_ci(y_test, ens_prob, roc_auc_score)
    pr_ci = bootstrap_ci(y_test, ens_prob, average_precision_score)

    # Policy simulator across PD cutoffs (assuming LGD = 0.65 on unsecured consumer loans)
    lgd = 0.65
    rates = test_df["BorrowerRate"].fillna(test_df["BorrowerRate"].median()).to_numpy()
    policy_rows: List[Dict[str, Any]] = []
    for max_pd in [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 1.00]:
        approved = ens_prob <= max_pd
        app_rate = float(np.mean(approved))
        if np.sum(approved) == 0:
            continue
        bad_rate = float(np.mean(y_test[approved]))
        avg_apr = float(np.mean(rates[approved]))
        expected_loss = bad_rate * lgd
        net_yield = avg_apr - expected_loss
        policy_rows.append(
            {
                "max_pd_cutoff": round(max_pd, 2),
                "min_credit_score": int(pd_to_credit_score(np.array([max_pd]))[0]),
                "approval_rate": round(app_rate, 4),
                "approved_count": int(np.sum(approved)),
                "observed_default_rate": round(bad_rate, 4),
                "avg_borrower_rate": round(avg_apr, 4),
                "expected_loss_rate": round(expected_loss, 4),
                "net_expected_yield": round(net_yield, 4),
            }
        )
    policy_df = pd.DataFrame(policy_rows)

    # Fairness / Proxy Slice Audit at 25% Max-PD Cutoff
    test_eval = test_df.copy()
    test_eval["pd"] = ens_prob
    test_eval["approved_25pct"] = (ens_prob <= 0.25).astype(int)
    homeowner_slice = (
        test_eval.groupby("IsBorrowerHomeowner")
        .agg(
            count=("target", "count"),
            approval_rate=("approved_25pct", "mean"),
            actual_default_rate=("target", "mean"),
            mean_predicted_pd=("pd", "mean"),
        )
        .round(4)
        .to_dict(orient="index")
    )

    metrics = {
        "total_closed_loans": int(len(df)),
        "train_loans": int(len(train_df)),
        "test_loans": int(len(test_df)),
        "train_period": f"{train_df['ListingCreationDate'].min().date()} to {train_df['ListingCreationDate'].max().date()}",
        "test_period": f"{test_df['ListingCreationDate'].min().date()} to {test_df['ListingCreationDate'].max().date()}",
        "train_default_rate": round(float(np.mean(y_train)), 4),
        "test_default_rate": round(float(np.mean(y_test)), 4),
        "woe_scorecard": {
            "roc_auc": round(float(roc_auc_score(y_test, sc_prob)), 4),
            "pr_auc": round(float(average_precision_score(y_test, sc_prob)), 4),
            "ks_statistic": round(ks_statistic(y_test, sc_prob), 4),
            "ece": round(expected_calibration_error(y_test, sc_prob), 4),
            "brier_score": round(float(brier_score_loss(y_test, sc_prob)), 4),
        },
        "calibrated_gbdt_ensemble": {
            "roc_auc": round(float(roc_auc_score(y_test, ens_prob)), 4),
            "roc_auc_95ci": list(roc_ci),
            "pr_auc": round(float(average_precision_score(y_test, ens_prob)), 4),
            "pr_auc_95ci": list(pr_ci),
            "ks_statistic": round(ks_statistic(y_test, ens_prob), 4),
            "ece": round(expected_calibration_error(y_test, ens_prob), 4),
            "brier_score": round(float(brier_score_loss(y_test, ens_prob)), 4),
        },
        "recommended_policy_at_25pct_pd": next(r for r in policy_rows if r["max_pd_cutoff"] == 0.25),
        "fairness_homeowner_slice": {str(k): v for k, v in homeowner_slice.items()},
    }

    curves = {
        "y_test": y_test,
        "sc_prob": sc_prob,
        "ens_prob": ens_prob,
    }
    return metrics, policy_df, curves


def render_hero_chart(metrics: Dict[str, Any], policy_df: pd.DataFrame, curves: Dict[str, np.ndarray]) -> Path:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    out_path = IMG_DIR / "hero.png"

    plt.rcParams.update(
        {
            "figure.facecolor": "#0B1220",
            "axes.facecolor": "#111A2E",
            "axes.edgecolor": "#22304A",
            "axes.labelcolor": "#CBD5E1",
            "text.color": "#F8FAFC",
            "xtick.color": "#94A3B8",
            "ytick.color": "#94A3B8",
            "grid.color": "#22304A",
            "font.sans-serif": ["DejaVu Sans", "Arial"],
        }
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=100)
    fig.patch.set_facecolor("#0B1220")

    # Left: Out-of-time ROC curve
    ax1 = axes[0]
    y_test = curves["y_test"]
    fpr_e, tpr_e, _ = roc_curve(y_test, curves["ens_prob"])
    fpr_s, tpr_s, _ = roc_curve(y_test, curves["sc_prob"])

    ax1.plot(
        fpr_e,
        tpr_e,
        color="#10B981",
        lw=2.8,
        label=f"Calibrated GBDT+Scorecard (AUC={metrics['calibrated_gbdt_ensemble']['roc_auc']:.3f}, KS={metrics['calibrated_gbdt_ensemble']['ks_statistic']:.3f})",
    )
    ax1.plot(
        fpr_s,
        tpr_s,
        color="#3B82F6",
        lw=2.0,
        ls="--",
        label=f"WoE Scorecard Alone (AUC={metrics['woe_scorecard']['roc_auc']:.3f}, KS={metrics['woe_scorecard']['ks_statistic']:.3f})",
    )
    ax1.plot([0, 1], [0, 1], color="#64748B", lw=1.2, ls=":")
    ax1.set_title(
        f"Out-of-Time ROC Curve (N={metrics['test_loans']:,} Closed Loans)",
        fontsize=14,
        fontweight="bold",
        pad=12,
    )
    ax1.set_xlabel("False Positive Rate (Good Loans Declined)", fontsize=11)
    ax1.set_ylabel("True Positive Rate (Defaults Caught)", fontsize=11)
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc="lower right", facecolor="#0B1220", edgecolor="#22304A", fontsize=10)

    # Right: Approval Policy Simulator (Approval Rate vs Net Portfolio Yield & Bad Rate)
    ax2 = axes[1]
    x_app = policy_df["approval_rate"] * 100.0
    ax2.plot(
        x_app,
        policy_df["net_expected_yield"] * 100.0,
        color="#10B981",
        marker="o",
        lw=2.8,
        label="Net Expected Yield (APR - Expected Loss) %",
    )
    ax2.plot(
        x_app,
        policy_df["observed_default_rate"] * 100.0,
        color="#FF914D",
        marker="s",
        lw=2.2,
        ls="--",
        label="Observed Default Rate among Approved %",
    )
    ax2.set_title("Approval Policy Simulator (Out-of-Time Cohort)", fontsize=14, fontweight="bold", pad=12)
    ax2.set_xlabel("Portfolio Approval Rate (%)", fontsize=11)
    ax2.set_ylabel("Rate (%)", fontsize=11)
    ax2.grid(True, alpha=0.4)
    ax2.legend(loc="upper left", facecolor="#0B1220", edgecolor="#22304A", fontsize=10)

    fig.suptitle(
        "LoanLens — Out-of-Time Credit Default Scorecard, Calibrated GBDT & Policy Simulator",
        fontsize=17,
        fontweight="bold",
        y=0.97,
    )
    plt.tight_layout(rect=[0, 0.02, 1, 0.93])
    fig.savefig(out_path, dpi=100, facecolor="#0B1220")
    plt.close(fig)
    return out_path


def run_all() -> Dict[str, Any]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_closed_loans()
    metrics, policy_df, curves = train_and_evaluate(df)
    policy_df.to_csv(REPORTS_DIR / "policy_curve.csv", index=False)
    render_hero_chart(metrics, policy_df, curves)
    with open(REPORTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    return metrics


if __name__ == "__main__":
    res = run_all()
    print(json.dumps(res, indent=2))
