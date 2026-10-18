# LinkedIn Post — LoanLens (Credit Risk Scorecard & Policy Simulator)

Whenever I see a credit-risk project reporting `0.96 AUC` on the Prosper loan dataset, I look for two things:
1. Did they leave post-origination payment columns (`LP_CustomerPayments`, `LoanCurrentDaysDelinquent`) in `X`?
2. Did they use a random train/test split across 2006–2014 instead of an out-of-time split?

Almost every time, the answer is yes.

I rebuilt my Prosper loan EDA into **LoanLens** — an out-of-time credit underwriting scorecard (`300–850` points) and approval policy simulator evaluated across **55,518 closed loans**.

What happens when you remove all 14 post-loan payment columns, exclude unfinished "Current" loans, and train strictly on `2005–2011` to test on future `2011–2014` originations (`N = 13,880`)?

1. **Honest out-of-time rank-ordering:** A monotonic quantile/WoE logistic scorecard + isotonic-calibrated GBDT reaches **ROC-AUC 0.707** (95% CI `0.696–0.715`) and **KS 0.305**, with Expected Calibration Error (ECE) of **0.043–0.055**.
2. **From probabilities to lending policy:** Approving every funded loan in the 2011–2014 test cohort yields a `30.67%` default rate and just `+1.28%` net yield (assuming 65% LGD). Setting a policy cutoff at **Max PD <= 25% (Credit Score >= 568)** approves **45.7% of applicants**, cuts the default rate nearly in half to **16.50%**, and lifts net expected portfolio yield to **+6.75%**.
3. **Governance & slice auditing:** Automated tests in CI block any post-origination column from entering the feature pipeline and audit approval-rate parity across borrower slices.

Code, out-of-time policy simulator, and tests: `https://github.com/ikebude/ai-ml-data-engineering/tree/main/machine-learning/prosper-loan-risk`

In credit risk, would you rather deploy a black-box model with a 0.02 higher AUC or a calibrated scorecard whose cutoffs a credit committee can simulate and explain?

#CreditRisk #DataScience #MachineLearning #FinTech #RiskManagement
