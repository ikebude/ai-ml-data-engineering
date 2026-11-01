# X (Twitter) Thread — Customer Intelligence

**1/6**
A churn score without Customer Lifetime Value (CLV) wastes retention budget on low-margin accounts.

I rebuilt my Customer Retention repo into **Customer Intelligence**: calibrated churn scoring + RFM segmentation + 6-month CLV backtesting (`pytest` verified in CI).

![Hero](img/hero.png)

**2/6**
On the 7,043-subscriber Telco benchmark (`26.54%` base churn):
- Logistic baseline: PR-AUC `0.831`, ROC-AUC `0.929`, Brier `0.112`
- Isotonic-calibrated GBDT: **PR-AUC `0.841`** (95% CI `0.807–0.871`), **ROC-AUC `0.933`**, **Brier `0.091`**

**3/6**
Why report Recall @ 20% contact budget instead of raw accuracy?
At 26.54% churn, calling 20% of customers can at most reach `20 / 26.54 = 75.4%` of churners even with a perfect oracle.
Our model catches **60.7% of all churners** inside that 20% budget (`80.5%` precision = `3.03x` lift).

**4/6**
Why calibration matters:
To rank outreach by `Expected 12m Revenue at Risk = 12 * MonthlyCharges * P(Churn)`, `P(Churn)` must be a true probability, not an uncalibrated score.
The top 50 holdout accounts alone represent **$60,669** in annualised revenue at risk.

**5/6**
For non-contract retail (a synthetic cohort generated in code), we run RFM quartile segmentation (`Champions`, `Loyal`, `At Risk High Value`, `Hibernating`) + 180-day out-of-time CLV backtesting.
Holdout total revenue error: **+1.19%** (`$15,849` predicted vs `$15,663` actual).

**6/6**
Full code, automated tests, and Streamlit action-list workbench:
https://github.com/ikebude/ai-ml-data-engineering/tree/main/machine-learning/customer-retention
