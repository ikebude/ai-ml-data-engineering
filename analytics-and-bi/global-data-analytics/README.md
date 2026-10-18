# Cross-Domain Exploratory Data Analytics Suite (Python, R & Power BI)

> Five cross-industry empirical studies spanning **30,871 records** across London Housing (`13,549` borough-month observations), Hourly Synoptic Weather (`8,784` hours), Netflix Content Catalog (`7,789` titles), Automotive Specifications (`428` vehicles), and Global COVID-19 Surveillance (`321` national snapshots)—implemented end-to-end in Python, R, and Power BI.

## Problem

Data teams frequently need to benchmark time-series, spatial, and catalog datasets across both **Python** (`pandas`, `matplotlib`, `seaborn`) and **R** (`tidyverse`, `ggplot2`, `rmarkdown`) before publishing executive views in **Power BI**. This repository consolidates five domain analyses to demonstrate reproducible cross-language data cleaning, statistical profiling, and dashboard delivery.

## Datasets & Multi-Language Modules

| Module Folder | Primary Dataset | Rows $\times$ Cols | Implementations Included |
|---|---|---:|---|
| **[`Housing Data Analysis/`](Housing%20Data%20Analysis)** | [`HouseData.csv`](Housing%20Data%20Analysis/HouseData.csv) (London Borough Monthly Housing & Crime, `1995–2019`) | `13,549 × 6` | Python (`.py`, `.ipynb`), R (`.R`), HTML/PDF Reports |
| **[`Weather Data Analysis/`](Weather%20Data%20Analysis)** | [`WeatherDataset.csv`](Weather%20Data%20Analysis/WeatherDataset.csv) (Full-Year Hourly Synoptic Telemetry, `366 days`) | `8,784 × 8` | Python (`.py`), R (`.R`, `.Rmd`, `.RData`), LaTeX/PDF |
| **[`Netflix Data Analytics/`](Netflix%20Data%20Analytics)** | [`Netflix-Dataset.csv`](Netflix%20Data%20Analysis/Netflix-Dataset.csv) (Global Streaming Catalog Metadata) | `7,789 × 11` | Python (`.py`, `.ipynb`), R (`.R`), Power BI (`.pbix`) |
| **[`Cars Data Analysis/`](Cars%20Data%20Analysis)** | [`CarsDataset.csv`](Cars%20Data%20Analysis/CarsDataset.csv) (Multi-Origin Vehicle MSRP, Invoice & Specs) | `428 × 15` | Python (`.py`, `.ipynb`), R (`.R`), Power BI (`.pbix`), PDF |
| **[`Covid 19 Data Analysis/`](Covid%2019%20Data%20Analysis)** | [`CovidData.csv`](Covid%2019%20Data%20Analysis/CovidData.csv) (Early-Wave Regional Case & Mortality Snapshot) | `321 × 6` | Python (`.py`), R (`.R`, `.Rmd`), Power BI (`.pbix`), HTML |

## Methodology

1. **Cross-Language Parity (Python $\leftrightarrow$ R):** Every module implements identical data-cleaning rules (duplicate deduplication, date parsing, currency stripping, and missing-value auditing) in both Python (`pandas`) and R (`dplyr`/`tidyr`) to ensure zero discrepancy between programmatic notebooks and Power BI (`Power Query M` / `DAX`) cards.
2. **Longitudinal & Distributional Profiling:** Computed 25-year compound price growth across London boroughs, 8,784-hour seasonal meteorological distributions, streaming catalog format ratios, and regional automotive pricing spreads.

## Key Quantitative Findings Across All 5 Domains

### 1. London Housing Market (`13,549` Monthly Records Across `45` Geographic Areas, `Jan 1995 – Sep 2019`)
- **Long-run valuation mean:** Across the 25-year panel (`Jan 1995` to `Sep 2019`), mean residential transaction price across all London boroughs and English regions is **£263,519.68**, with inner-London boroughs (`Kensington and Chelsea`, `Westminster`, `Camden`) driving extreme right-tail divergence post-2009.
- **Volume vs Price decoupling:** Monthly `houses_sold` contracted sharply during the 2008–2009 Global Financial Crisis before recovering at lower unit turnover despite record nominal price appreciation.

### 2. Hourly Synoptic Weather Telemetry (`8,784` Consecutive Hours, Leap-Year Cycle)
- **Thermal & atmospheric bounds:** Across all `8,784` hourly readings (`366 days × 24 hours`), ambient temperature spans **$-23.3^\circ\text{C}$ to $+33.0^\circ\text{C}$** with an annual mean of **$+8.80^\circ\text{C}$**, relative humidity averages **`67.43%`**, wind speed averages **`14.95 km/h`**, visibility averages **`27.66 km`**, and station pressure averages **`101.05 kPa`**.

### 3. Netflix Global Content Catalog (`7,789` Titles)
- **Format split (`69.06%` Movies vs `30.94%` TV Shows):** Of the `7,789` catalog records, **5,379 (`69.06%`) are Movies** and **2,410 (`30.94%`) are TV Shows**, with catalog additions accelerating sharply between 2016 and 2020 and the United States and India serving as the top two production origins.

### 4. Automotive Specifications & Pricing (`428` Vehicles)
- **Origin price hierarchy:** Mean `MSRP` across all 428 vehicles is **\$32,774.86** (`median \$27,635.00`) with an **8.06%** average dealer margin over `Invoice`. European marques command a **\$40,590** median MSRP versus **\$25,520** for US marques and **\$23,032.50** for Asian marques (`24.83` combined MPG). *(See [`machine-learning/cars-model-analysis`](../../machine-learning/cars-model-analysis) for the upgraded hedonic regression pipeline).*

### 5. Early-Wave COVID-19 Global Surveillance Snapshot (`321` Regional Records)
- **Case fatality & recovery baseline:** Across the `321` regional/national snapshot records (`as of April 29, 2020`), cumulative totals capture **3,193,886 confirmed cases**, **227,638 deaths** (`7.13%` crude case-fatality ratio among closed/reported early-wave cases), and **972,719 recovered cases** (`30.46%` recovered share).

## Executive Recommendations

1. **Standardize Ingestion Pipelines on Parquet + Schema Contracts:** Replace ad-hoc CSV/Excel reads across R and Python scripts with typed schema validation so date formatting (`1/1/1995` vs ISO-8601) and currency strings (`$36,945`) are normalized once upstream of Power BI.
2. **Promote Explanatory EDA into Predictive Pipelines:** Transition static descriptive workbooks into automated regression/classification pipelines (as demonstrated in the companion [`cars-model-analysis`](../../machine-learning/cars-model-analysis) hedonic pricing package).

## How to Open / Run

```bash
# Run any of the Python EDA scripts from the repository root
python "Housing Data Analysis/London House Data Script.py"
python "Netflix Data Analytics/NETFLIX Analysis.py"
python "Weather Data Analysis/Weather EDA (Python).py"
```

To inspect the interactive dashboards, open [`Cars Dashboard.pbix`](Cars%20Data%20Analysis/Cars%20Dashboard.pbix), [`Covid 19 Dashboard.pbix`](Covid%2019%20Data%20Analysis/Covid%2019%20Dashboard.pbix), or [`NETFLIX Dashboard.pbix`](Netflix%20Data%20Analytics/NETFLIX%20Dashboard.pbix) in **Power BI Desktop**.

## Post kit

- [`POST_LINKEDIN.md`](POST_LINKEDIN.md) — Lessons from maintaining cross-language analytical parity across Python, R, and Power BI on 30,871 records.
- [`POST_X.md`](POST_X.md) — 6-tweet summary of key quantitative findings across all 5 datasets.