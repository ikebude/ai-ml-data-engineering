Why do the heaviest-mileage drivers on a navigation app churn the fastest?

When I built an end-to-end churn prediction pipeline on 14,299 Waze users (`17.74%` monthly churn rate), the behavioral data surfaced a counterintuitive pattern that plain accuracy metrics completely hide:

1. **The Long-Haul Churn Paradox:** Churned users actually log **59.2% more kilometers per driving day** (`407.60 km/day` median) than retained users (`256.06 km/day`), but they only open the app on `6.0` driving days per month compared to `14.0` days for retained daily commuters. Waze's core retention engine is built around daily urban traffic avoidance, not episodic highway trips.
2. **Linear Signal Dominance:** Permutation importance showed that `activity_days` (`0.1474` PR-AUC drop) and onboarding tenure (`0.0407` PR-AUC drop) carry the overwhelming majority of predictive signal. As a result, a well-scaled Logistic Regression baseline (`PR-AUC 0.3785`, `ROC-AUC 0.7447`) matched Isotonic-Calibrated HistGradientBoosting (`PR-AUC 0.3790`, 95% CI `[0.3382, 0.4193]`).
3. **Actionable Contact Budgets:** Instead of spamming 100% of users, targeting just the top 10% highest-risk cohort achieves **47.55% precision** (a **2.68x lift** over random targeting) and captures **26.82%** of all churning users; expanding to a 20% contact budget captures **43.00% recall**.

Visual: Precision-Recall curve & Permutation PR-AUC drop across all 15 engineered telemetry features (`img/hero.png`).

When your team evaluates churn models, do you optimize for global ROC-AUC or recall at your exact marketing contact capacity?

#MachineLearning #DataScience #ChurnPrediction #CustomerRetention #BI
