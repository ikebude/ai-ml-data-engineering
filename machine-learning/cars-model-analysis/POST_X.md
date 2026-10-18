1/6 A classic trap in automotive pricing datasets: leaving `Invoice` in `X` when predicting `MSRP`. Since dealer invoice is ~92% of MSRP, your model gets R² = 0.99 without learning a single mechanical spec.

I built a leak-free hedonic pricing pipeline on 428 vehicles. Here's what drives MSRP. 🧵👇

2/6 Feature engineering & leakage firewall:
• Stripped currency formatting (`$`, `,`) and imputed missing rotary-engine cylinders.
• Engineered `power_to_weight` (hp / 1,000 lbs) and EPA `mpg_combined` (0.55 City + 0.45 Hwy).
• Excluded `Invoice` and `dealer_margin_pct` from the predictor matrix (verified via unit test).

3/6 Out-of-sample test results (80/20 origin-stratified split, n=86):
• Log-Ridge Baseline: MAE $4,826.78 | RMSE $7,226.65 | MAPE 14.32% | R² 0.8403
• Gradient Boosting: MAE $4,189.54 (95% CI [$3,177, $5,305]) | MAPE 12.28% | R² 0.8659
13.2% reduction in dollar MAE.

4/6 What actually drives vehicle sticker price? (Permutation R² drop on test set):
1. Horsepower: -0.6949 R²
2. Regional Origin: -0.1640 R²
3. Curb Weight: -0.1090 R²
4. Vehicle Type: -0.0359 R²
5. Highway MPG: -0.0262 R²

5/6 Regional & Body-Type Economics across all 428 cars:
• Median MSRP: Europe $40,590 vs USA $25,520 vs Asia $23,033.
• Combined MPG: Asia 24.83 MPG vs USA 22.20 MPG vs Europe 22.01 MPG.
• Dealer Gross Margin ((MSRP - Invoice)/MSRP): Averages 8.06%, highest on Trucks (9.03%) & Sports (8.94%), lowest on Wagons (7.38%).

6/6 Full pipeline (`src/pipeline.py`), pytest suite, and `reports/metrics.json` are live in `machine-learning/cars-model-analysis`.
