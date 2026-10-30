How much of a car's sticker price (`MSRP`) comes from what is under the hood versus where the badge was made?

I built a hedonic pricing pipeline across 428 vehicles (38 manufacturers, 6 body styles) to predict MSRP strictly from mechanical specifications and origin—explicitly walling off dealer `Invoice` cost so the model couldn't cheat:

1. **Horsepower + Origin Dominate Valuation:** Permutation importance on the held-out test split showed that `Horsepower` (`0.6922` $R^2$ drop), `Origin` (`0.1641` $R^2$ drop), and curb `Weight` (`0.1091` $R^2$ drop) are the three pillars of retail vehicle pricing.
2. **The 76% European Sticker Premium:** European vehicles carry a median MSRP of **\$40,590** (`mean \$48,350`)—**59.1% above** US models (`median \$25,520`) and **76.2% above** Asian models (`median \$23,033`), while Asian powertrains lead combined fuel economy at **24.83 MPG** (`vs 22.01 MPG` for Europe).
3. **Dealer Margin Compression & Model Accuracy:** Training a `GradientBoostingRegressor` in log-MSRP space achieved **$R^2 = 0.8660$** and **12.27% MAPE** (`MAE \$4,186.99`, beating the Log-Ridge baseline's `\$4,826.78` MAE by **13.3%**). Meanwhile, descriptive margin auditing revealed that dealer gross margins average **8.06%** overall, peaking on **Trucks (9.03%)** and **Sports cars (8.94%)** and compressing on **Wagons (7.38%)** and **Hybrids (7.46%)**.

Visual: Out-of-sample MSRP calibration and permutation $R^2$ feature importance (`img/hero.png`).

When modeling skewed pricing targets like vehicles or real estate, do you prefer log-transformed tree ensembles or Gamma/Tweedie deviance loss?

#MachineLearning #PricingAnalytics #DataScience #Automotive #Regression
