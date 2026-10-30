GICS sector labels tell you what a company sells—not how its balance sheet behaves.

To look beneath standard sector labels, I ran a quantitative factor clustering and robust anomaly detection pipeline across all 502 S&P 500 constituents (\$55.58 trillion aggregate market cap):

1. **Extreme Top-Heavy Concentration:** Just 10 companies now command **40.12%** of total S&P 500 market capitalization. Technology (\$17.29T, `31.10%` index weight) and Communication Services (\$7.80T, `14.04%` weight) together represent **45.14%** of the entire benchmark.
2. **Three Fundamental Regimes (Silhouette `0.3700`):** Across PCA-projected financial ratios (`52.00%` variance in 2D, `67.73%` in 3D), K-Means cleanly separates the index into:
   - **70 High-Multiple Compounders:** Median market cap `\$131.89B`, Price/EBITDA `43.15x`, and `+15.10%` median YoY revenue growth.
   - **371 Core Cash-Flow Constituents:** Median market cap `\$36.90B`, Price/EBITDA `12.39x`, and `+4.50%` revenue growth.
   - **61 Deep-Value / Labor-Intensive Cyclicals:** Median market cap `\$16.09B`, Price/EBITDA `5.55x`, and `+1.30%` revenue growth.
3. **Non-Linear Fundamental Scaling:** Predicting market-cap tier strictly from operational fundamentals (excluding market cap and index weight) jumped from **0.6562 Macro-F1** (Logistic Regression) to **0.8692 Macro-F1** (Random Forest, 95% CI `[0.8405, 0.8996]`).

Visual: 2D PCA factor projection & GICS sector market-cap distribution (`img/hero.png`).

When building equity risk models, do you rely on GICS sectors or statistical factor clusters?

#QuantitativeFinance #MachineLearning #DataScience #SP500 #PortfolioAnalytics
