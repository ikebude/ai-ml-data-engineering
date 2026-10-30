# LinkedIn Post — Customer Intelligence (Churn, RFM & CLV)

Most churn models answer the wrong question.

They tell a retention manager *who* is likely to cancel, but not **who is worth calling first** when the call centre only has bandwidth to reach 20% of the customer base.

I rebuilt my telecom and retail retention analysis into **Customer Intelligence** — an end-to-end Python pipeline and Streamlit workbench that combines calibrated churn scoring, RFM segmentation, and 6-month Customer Lifetime Value (CLV) backtesting.

Three takeaways from the benchmark (`7,043` subscribers, `26.54%` base churn rate):

1. **Calibrated probabilities matter when money is attached:** Isotonic-calibrated HistGradientBoosting reached **PR-AUC 0.841** (95% CI `0.807–0.871`), **ROC-AUC 0.933**, and cut Brier calibration error from `0.112` (logistic baseline) to **`0.091`**.
2. **Respecting operational capacity:** Because 26.54% of the cohort churns, a team that can only call 20% of customers has a theoretical maximum recall of `75.4%`. At a 20% contact budget, the model captures **60.7% of all churners** with an **80.5% hit rate** (`3.03x` lift over random outreach).
3. **Revenue at risk > raw probability:** Ranking the holdout queue by `P(Churn) × 12-Month Contract Value` isolates **$60,669 in annualised revenue at risk** across just the top 50 accounts—primarily month-to-month fiber subscribers with unresolved technical tickets.

On the transactional cohort backtest (`1,200` customers, 360d calibration / 180d holdout), the analytical CLV estimator landed within **+1.19%** of actual 6-month holdout revenue (`$15,849` predicted vs `$15,663` actual).

Code, tests, and action-list exporter: `https://github.com/ikebude/ai-ml-data-engineering/tree/main/machine-learning/customer-retention`

When your team prioritises retention outreach, do you rank by churn probability alone or expected value at risk?

#DataScience #MachineLearning #CustomerRetention #BusinessIntelligence #Python
