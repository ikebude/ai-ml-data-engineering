# LoanLens — Out-of-Time Credit Default Scorecard, Calibrated GBDT & Policy Simulator

> **One-line result:** Scores consumer loan applications `300–850` using strictly pre-origination bureau features across `55,518` closed Prosper loans — reaching **out-of-time ROC-AUC 0.705** (95% CI `0.6945–0.7137`) and **KS 0.303** on future origination cohorts (`2011–2014`), cutting portfolio default rates from **30.67% to 16.92%** at a **25% Max-PD policy cutoff** (`+6.61%` net expected yield after 65% LGD).

| Product Workspace UI | Out-of-Time ROC & Policy Simulator (`img/hero.png`) |
|---|---|
| ![LoanLens UI](img/ui-preview.png) | ![LoanLens Benchmark](img/hero.png) |

---

## Problem

Many credit-risk notebooks on the Prosper dataset report inflated `0.95+` accuracy or AUC because they accidentally include **post-origination payment columns** (`LP_CustomerPayments`, `LoanCurrentDaysDelinquent`, `ClosedDate`) or evaluate on a random split that mixes 2006 and 2013 macro regimes. Furthermore, credit committees do not make decisions from an ROC curve alone—they need a **calibrated probability of default (PD)**, an interpretable **300–850 scorecard**, and an **approval policy cutoff simulator** that trades off approval volume against expected credit loss.

**LoanLens** upgrades our original Prosper exploratory analysis into a leak-free, out-of-time underwriting and policy simulation product.

---

## Data

- **Source:** Prosper Peer-to-Peer Lending Dataset (`Prosperloandata.csv` — `113,937` total listings, `81` columns).

> Note: the raw 84 MB CSV is tracked in git history; it is kept as is (no history rewrite). New large data should use Git LFS or a download script.
- **Closed-Loan Filtering (Preventing Censoring Bias):** Active `"Current"` loans whose 36- or 60-month term has not finished are excluded so recent cohorts are not falsely labelled as non-defaults. The filtered closed-loan cohort contains **`55,518` completed or defaulted loans**:
  - `1` (**Bad / Default**): `Defaulted`, `Chargedoff`, `Past Due (>60 days)`
  - `0` (**Good / Completed**): `Completed`
- **Out-of-Time (OOT) Chronological Split:**
  - **Training Cohort (75%):** `41,638` loans originated `2005-11-09` to `2011-09-19` (`31.99%` default rate).
  - **Out-of-Time Test Cohort (25%):** `13,880` loans originated `2011-09-19` to `2014-02-13` (`30.67%` default rate).
- **Strict Anti-Leakage Gate:** `tests/test_loanlens.py` verifies that all `14` post-origination payment/recovery fields (`LP_*`, `LoanCurrentDaysDelinquent`, `ClosedDate`, `LoanFirstDefaultedCycleNumber`) are excluded prior to feature engineering.

---

## Approach

1. **Pre-Origination Feature Engineering (`src/loanlens.py`):**
   - Harmonises pre-2009 `CreditGrade` and post-2009 `ProsperRating (numeric)` into a unified origination rating (`unified_rating`), computes `credit_score_mid` from bureau lower/upper bounds, and calculates monthly `payment_to_income` burden alongside 28 bureau and utilization attributes (`BankcardUtilization`, `InquiriesLast6Months`, `DebtToIncomeRatio`, `DelinquenciesLast7Years`).
2. **Dual Architecture (Regulated Scorecard vs Calibrated GBDT):**
   - **Monotonic Quantile/WoE Logistic Scorecard:** Transforms continuous bureau attributes into 10 quantile bins + L2-regularised logistic regression with isotonic calibration, mapped to a **`300–850` credit score** (`PDO = 20` points per doubling of odds at `600`).
   - **Calibrated GBDT + Scorecard Ensemble:** Combines isotonic-calibrated `HistGradientBoostingClassifier` (70%) with the logistic scorecard (30%) for higher non-linear rank-ordering while preserving smooth probability calibration.
3. **Approval Policy Cutoff Simulator:**
   - Sweeps maximum allowable PD from `10%` to `100%` on the `13,880` out-of-time test loans, calculating approval rate, observed bad rate, expected loss (`Bad Rate × 65% LGD`), and net expected portfolio yield (`Average Borrower APR − Expected Loss`).

---

## Results

Reproduce: python3.11, pinned `requirements.txt`, `pytest -q` (regenerates `reports/`).

### 1. Out-of-Time Model Performance (`2011-09-19` to `2014-02-13`, `N = 13,880`)

| Metric | WoE / Quantile Logistic Scorecard | Calibrated GBDT + Scorecard | 95% Bootstrap CI |
|---|---:|---:|---:|
| **Out-of-Time ROC-AUC** *(target `>= 0.70`)* | `0.6673` | **`0.7049`** | `0.6945 – 0.7137` |
| **Out-of-Time KS Statistic** *(target `>= 0.30`)* | `0.2413` | **`0.3034`** | — |
| **Out-of-Time PR-AUC** *(base rate `0.3067`)* | `0.4390` | **`0.4791`** | `0.4643 – 0.4950` |
| **Expected Calibration Error (ECE)** | **`0.0430`** | `0.0565` | — |
| **Brier Score** | `0.1988` | **`0.1946`** | — |

> **Why OOT ROC-AUC is ~0.70 (and why that is realistic):** Prosper underwent a major structural shift between 2005–2008 (pre-SEC registration) and 2011–2014 (post-relaunch credit policy), and borrower credit scores are already pre-screened by Prosper's platform floor. On strictly pre-origination features across a multi-year macro shift, an out-of-time `ROC-AUC` of `0.705` and `KS` of `0.303` reflects genuine bureau signal without payment-history leakage.

### 2. Approval Policy Simulator (`reports/policy_curve.csv`)

| Max PD Cutoff | Min Credit Score (`300–850`) | Approval Rate | Approved Loans | Observed Default Rate | Avg Borrower APR | Expected Loss (`65%` LGD) | Net Expected Yield |
|---:|---:|---:|---:|---:|---:|---:|---:|
| `0.15` | `587` | `18.51%` | `2,569` | `7.55%` | `12.31%` | `4.91%` | **`+7.40%`** |
| `0.20` | `577` | `31.64%` | `4,391` | `12.62%` | `15.10%` | `8.20%` | **`+6.90%`** |
| **`0.25` (Recommended)** | **`568`** | **`46.41%`** | **`6,442`** | **`16.92%`** | **`17.61%`** | **`11.00%`** | **`+6.61%`** |
| `0.30` | `561` | `63.36%` | `8,794` | `21.59%` | `19.65%` | `14.04%` | **`+5.61%`** |
| `1.00` *(Approve All)* | `300` | `100.00%` | `13,880` | `30.67%` | `22.15%` | `19.94%` | `+2.22%` |

### 3. Fairness & Proxy Slice Audit (at `25%` Max-PD Cutoff)

Protected demographic attributes are excluded from training. Auditing the `25%` Max-PD policy across `IsBorrowerHomeowner` on the out-of-time test cohort shows an approval-rate gap of just **`1.82` percentage points** (`45.49%` non-homeowners vs `47.31%` homeowners), tracking the underlying default rate differential (`32.89%` vs `28.50%`).

> **Deployment Governance Note:** This model is trained on US consumer peer-to-peer loans. Before deploying LoanLens for Nigerian microfinance banks or digital lenders, the scorecard must be retrained and recalibrated on local CRC/FirstCentral bureau data and NGN bank-statement cashflow features.

---

## Limitations

- Only loans that had closed by the data snapshot are used. For the 2011–2014 test cohort this keeps loans that ended early (early defaults and early payoffs), so the test default rate and AUC describe that subset, not every loan originated then.
- `BorrowerRate`, `ProsperRating` and `ProsperScore` are Prosper's own risk pricing at origination. They are legitimately pre-origination, but part of the lift comes from reusing Prosper's model rather than raw bureau data.
- The GBDT ensemble ranks better but is less well calibrated than the scorecard (ECE `0.0565` vs `0.0430`). PD cutoffs from the ensemble should be recalibrated before being treated as true default probabilities.
- Net expected yield is `average APR − default rate × 65% LGD`. It ignores interest collected before default, the timing of recoveries, fees and funding cost, so it compares policies with each other; it is not a forecast of portfolio return.
- `IsBorrowerHomeowner` is a proxy slice, not a protected attribute; the dataset has none, so this is not a full fair-lending review.

## What I'd Do Next

1. **Reject Inference:** Incorporate declined/unfunded listing applications via parceling or fuzzy augmentation to correct for selection bias in funded loans.
2. **Macroeconomic Covariates:** Join state-level unemployment rate and Federal Funds rate at origination month to stabilise calibration across credit cycles.
3. **Bank-Statement Cashflow Module:** Combine bureau scorecard points with 90-day transaction cashflow volatility for thin-file emerging-market borrowers.

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the out-of-time training, scorecard calibration & policy simulator
python -m src.loanlens

# 3. Run the anti-leakage and monotonic scorecard test suite
python -m pytest -q

# 4. Launch the interactive Streamlit underwriting & policy simulator app
streamlit run app.py
```

---

## Post Kit

- [`POST_LINKEDIN.md`](POST_LINKEDIN.md) — Why 0.95+ AUC credit-risk notebooks are almost always leaking post-loan payments, and how an out-of-time policy simulator works.
- [`POST_X.md`](POST_X.md) — 6-tweet thread on out-of-time scorecard calibration & policy simulation.
- [`img/hero.png`](img/hero.png) & [`img/ui-preview.png`](img/ui-preview.png) — High-resolution visuals.