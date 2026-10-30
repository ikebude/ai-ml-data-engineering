How do you price an upfront taxi fare before the cab even moves—without accidentally leaking post-trip data into your training pipeline?

In many public NYC TLC taxi analyses, models achieve "99% R²" because they leave `total_amount`, `tip_amount`, or `tpep_dropoff_datetime` in the feature matrix. In production, none of those exist when a rider requests a quote.

I rebuilt the NYC TLC Yellow Taxi pricing pipeline across 22,441 clean trips using a strict pre-dispatch feature firewall and an out-of-time chronological split (training on Jan–Oct 2017, testing on 4,489 trips in Oct–Dec 2017):

1. **29.6% Lower Fare Error:** Switching from a Linear Ridge baseline to `HistGradientBoostingRegressor` cut out-of-time Fare MAE from **\$2.09 to \$1.47** (95% CI `[$1.42, $1.54]`) and raised $R^2$ from `0.9071` to `0.9499`.
2. **Upfront Quote Precision:** **53.22%** of out-of-time quotes land within **±\$1.00** of the final metered fare (up from `33.21%` with Ridge), and **77.23%** land within **±\$2.00**.
3. **Congestion-Aware Duration Modeling:** Using only pre-trip origin/destination zones, distance, and pickup hour, the model cut trip duration MAE by **27.4%** (`3.64 minutes` vs `5.01 minutes` baseline, $R^2 = 0.7827$), accurately tracking Manhattan's diurnal rush-hour slowdown.

Visual: Out-of-time fare calibration and 24-hour diurnal duration profile (`img/hero.png`).

How does your team enforce feature firewalls to prevent subtle timestamp or settlement leakage in time-series tabular models?

#MachineLearning #DataEngineering #PricingModels #TimeSeries #NYCTLC
