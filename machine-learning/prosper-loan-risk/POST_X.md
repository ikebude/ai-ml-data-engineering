# X (Twitter) Thread — LoanLens Credit Risk & Policy Simulator

**1/6**
Why do so many credit-risk notebooks claim `0.95+ AUC` on the Prosper dataset?
Because they leak post-origination payment columns (`LP_CustomerPayments`) and shuffle 2006 and 2013 loans together.

I built **LoanLens** to show what real out-of-time underwriting looks like on 55,518 closed loans.

![Hero](img/hero.png)

**2/6**
Rule 1: Exclude active "Current" loans whose 36/60m term hasn't finished (censoring bias).
Rule 2: Drop all 14 post-origination payment & recovery columns (enforced by a unit test in CI).
Rule 3: Chronological split — train on `2005–2011` (`41,638` loans), test out-of-time on `2011–2014` (`13,880` loans).

**3/6**
Out-of-time results on the 13,880 future loans (`30.67%` base default rate):
- WoE/Quantile Logistic Scorecard (`300–850` scale, PDO=20): ROC-AUC `0.667`, ECE `0.043`
- Calibrated GBDT + Scorecard Ensemble: **ROC-AUC `0.705`** (95% CI `0.694–0.714`), **KS `0.303`**, **PR-AUC `0.479`**

**4/6**
An ROC curve isn't a lending policy. Credit committees need an **Approval Policy Simulator**:
- Approve all (`PD <= 100%`): `30.67%` default rate -> `+2.22%` net yield (at 65% LGD)
- **Cutoff at `PD <= 25%` (`Score >= 568`)**: approves `46.4%` of loans, cuts defaults to **`16.92%`**, and lifts net expected yield to **`+6.61%`**.

**5/6**
We also audit proxy slices at the `25%` PD cutoff: homeowner vs non-homeowner approval rates differ by just `1.82` percentage points (`47.3%` vs `45.5%`), tracking true default differences (`28.5%` vs `32.9%`).

**6/6**
Code, Streamlit policy simulator, and CI tests:
https://github.com/ikebude/ai-ml-data-engineering/tree/main/machine-learning/prosper-loan-risk
