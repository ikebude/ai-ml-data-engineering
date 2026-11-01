1/6 If your NYC Taxi fare model has R² = 0.999, check your columns—you probably leaked `total_amount` or `tpep_dropoff_datetime`.

I built a leak-free, out-of-time upfront fare & duration estimator on 22,441 NYC Yellow Taxi trips. Here are the real numbers. 🧵👇

2/6 Data hygiene & pre-trip firewall:
• Filtered 20 non-positive fares and 148 zero-distance meter errors from 22,699 raw trips.
• Banned all post-trip columns (`total_amount`, `tip_amount`, `tolls_amount`, `dropoff_datetime`).
• Strictly chronological 80/20 split: Train Jan–Oct 2017 (17,952 trips) → Test Oct–Dec 2017 (4,489 trips).

3/6 Metered Fare (`fare_amount`, $) on the Q4 out-of-time test set:
• Linear Ridge baseline: MAE $2.09 | RMSE $3.31 | R² 0.9071
• HistGradientBoosting: MAE $1.47 (95% CI [$1.42, $1.54]) | RMSE $2.43 | R² 0.9499
That's a 29.6% reduction in MAE.

4/6 Why does tree boosting beat linear regression by $0.62/trip when distance is linear?
1) JFK flat-rate rules (`RatecodeID = 2`) break linear distance scaling.
2) Rush-hour traffic makes time-on-meter dominate distance-on-meter in Midtown corridors.

5/6 Pre-trip Duration (`trip_duration_min`) results on the same out-of-time split:
• Linear Ridge: MAE 5.01 min | RMSE 7.49 min | R² 0.6395
• HistGradientBoosting: MAE 3.64 min (95% CI [3.51, 3.78]) | RMSE 5.82 min | R² 0.7827

6/6 Code, automated leakage tests (`pytest -q`), and bootstrap CI reports (`reports/metrics.json`) are in `machine-learning/tlc-cab-fare-intelligence`.
