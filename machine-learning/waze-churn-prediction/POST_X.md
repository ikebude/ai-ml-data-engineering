1/6 Most churn notebooks stop at "82% accuracy!" on an 18% churn dataset—which you can get by predicting zero churn for everyone.

I rebuilt the Waze User Churn pipeline (14,299 labeled users) around the metrics retention teams actually buy: PR-AUC, calibration, and Recall @ K% contact rate. 🧵👇

2/6 First, the behavioral paradox in the telemetry:
Churned users drive 59.2% MORE kilometers per driving day than retained users (median 407.60 km vs 256.06 km), but on less than half the days (6.0 vs 14.0 driving days/month).
Highway marathoners churn; daily traffic commuters stay.

3/6 Second, device parity:
iPhone churn is 17.83% vs 17.56% on Android. And `device_encoded` has near-zero permutation importance. The churn problem is behavioral habit formation, not an OS bug.

4/6 Third, Baseline vs Gradient Boosting (20% stratified test split, n=2,860):
• Logistic Regression: PR-AUC 0.3785 | ROC-AUC 0.7447 | Brier 0.1291
• Isotonic HistGradientBoosting: PR-AUC 0.3755 (95% CI [0.3346, 0.4169])
Why so close? `activity_days` (-0.1450 PR-AUC when permuted) and tenure (-0.0398) act almost monotonically in log-odds space.

5/6 Decision impact at fixed marketing budgets:
• Top 10% contact budget → 47.55% precision (2.68x lift over 17.73% base rate), capturing 26.82% of all churners.
• Top 20% contact budget → captures 43.00% of all churners (95% CI [39.43%, 46.63%]).

6/6 Full reproducible pipeline (`src/pipeline.py`), pytest suite, and bootstrap confidence intervals in `reports/metrics.json` are live in my portfolio repo.
