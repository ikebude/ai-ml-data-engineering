1/6 How concentrated is the S&P 500, and what happens when you cluster all 502 companies by financial ratios instead of GICS labels?

I built a reproducible PCA + K-Means + MAD anomaly pipeline on the $55.58T index. Here is what the data shows. 🧵👇

2/6 Concentration reality check:
• Aggregate S&P 500 market cap: $55.58 Trillion across 502 constituents.
• Top 10 companies share: 40.12% of the entire index.
• Top 3 sectors: Technology ($17.29T, 31.10%), Communication Services ($7.80T, 14.04%), Financial Services ($7.11T, 12.79%) = 57.93% combined.

3/6 Unsupervised Factor Regimes (StandardScaler → PCA → K-Means):
Evaluating k ∈ {3,4,5,6} via Silhouette score peaks at k=3 (0.3700; 2D PCA captures 52.00% variance, 3D captures 67.73%).

4/6 The 3 S&P 500 Regimes:
• Cluster 0 (n=70): High-Multiple Compounders — Median MCap $131.89B | P/EBITDA 43.15x | YoY Rev Growth +15.10%
• Cluster 1 (n=371): Core Cash-Flow — Median MCap $36.90B | P/EBITDA 12.39x | Rev Growth +4.50%
• Cluster 2 (n=61): Deep-Value Cyclicals — Median MCap $16.09B | P/EBITDA 5.55x | Rev Growth +1.30%

5/6 Robust MAD Z-Score Outliers:
Using Median Absolute Deviation (scale = 1.4826 × MAD) flags structural outliers like unsplit share-price leaders (NVR Z=81.35, BKNG Z=49.16, AZO Z=31.26) and outlier names (SMCI Z=17.07, CRWD Z=16.52, JPM Z=16.52).

6/6 Supervised benchmark: predicting Market-Cap Tercile purely from operational fundamentals (5-fold CV):
• Logistic Regression: 0.6562 Macro-F1
• Random Forest: 0.8692 Macro-F1 (95% CI [0.8405, 0.8996])
Code & tests in `machine-learning/sp500-analysis`.
