# Relational Customer Valuation & Multi-Platform BI Suite (KPMG Sprocket Central & PwC Retention)

> Audits 20,000 retail cycling transactions (\$21.95M approved revenue, \$10.83M gross margin across 4,000 existing and 1,000 prospective customers) plus 7,043 telecom retention records to rank high-LTV expansion segments across Python, R, Tableau, and Power BI.

## Problem

Sprocket Central Pty Ltd (KPMG Data Analytics Consulting Case Study) possessed 20,000 historical transactions and 4,000 customer demographic/address records alongside an unranked lead list of 1,000 new customers—but suffered from severe schema quality defects (inconsistent state codes, unparsed currency strings, phantom `1843` birth dates, and orphaned foreign keys) that blocked reliable customer lifetime value (LTV) targeting. In parallel, the PwC Customer Retention module required cross-validating churn risk drivers in R, Python, and Power BI.

## Datasets & Repository Structure

1. **[`KPMG Data Analytics (Relational Database)/`](KPMG%20Data%20Analytics%20(Relational%20Database))**
   - [`Transactions.csv`](KPMG%20Data%20Analytics%20(Relational%20Database)/KPMG_Dataset/Transactions.csv) — **20,000** transactions (`19,821` `Approved`, `179` `Cancelled`) with `list_price`, `standard_cost`, `brand`, `product_line`, `product_class`, `product_size`, and `online_order`.
   - [`CustomerDemographic.csv`](KPMG%20Data%20Analytics%20(Relational%20Database)/KPMG_Dataset/CustomerDemographic.csv) — **4,000** customer profiles (`AGE`, `gender`, `past_3_years_bike_related_purchases`, `job_industry_category`, `wealth_segment`, `owns_car`, `tenure`).
   - [`CustomerAddress.csv`](KPMG%20Data%20Analytics%20(Relational%20Database)/KPMG_Dataset/CustomerAddress.csv) — **3,999** customer locations across Australian states (`NSW`, `VIC`, `QLD`) and `property_valuation` tiers (`1–12`).
   - [`NewCustomerList.csv`](KPMG%20Data%20Analytics%20(Relational%20Database)/KPMG_Dataset/NewCustomerList.csv) — **1,000** unranked prospective leads scored for marketing acquisition.
   - Deliverables: [`Kpmg python Data Analytics.ipynb`](KPMG%20Data%20Analytics%20(Relational%20Database)/Kpmg%20python%20Data%20Analytics.ipynb), [`KPMG_Analysis(R).Rmd`](KPMG%20Data%20Analytics%20(Relational%20Database)/KPMG_Analysis(R).Rmd), [`KPMG Dashboard.pbix`](KPMG%20Data%20Analytics%20(Relational%20Database)/KPMG%20Dashboard.pbix), and Tableau packaged workbook [`Example dashboard2.twbx`](KPMG%20Data%20Analytics%20(Relational%20Database)/KPMG_VI_Model_Works/Example%20dashboard2.twbx).
2. **[`Customer Retention Analysis/`](Customer%20Retention%20Analysis)**
   - [`ChurnDataset.xlsx`](Customer%20Retention%20Analysis/ChurnDataset.xlsx) (`7,043` subscribers), R Markdown report [`Churn EDA(R).Rmd`](Customer%20Retention%20Analysis/Churn%20EDA(R).Rmd), Python notebook [`Customer Retention EDA.ipynb`](Customer%20Retention%20Analysis/Customer%20Retention%20EDA.ipynb), and [`Churn Analysis Dashboard.pbix`](Customer%20Retention%20Analysis/Churn%20Analysis%20Dashboard.pbix).

## Methodology: Relational Data Quality Audit & Margin Modeling

1. **Entity Resolution & Schema Remediation (Module 1 Audit):**
   - Standardized inconsistent `gender` labels (`F`, `Femal` $\rightarrow$ `Female`; `M` $\rightarrow$ `Male`; `U` $\rightarrow$ `Unknown`) and Australian `state` codes (`New South Wales` $\rightarrow$ `NSW`, `Victoria` $\rightarrow$ `VIC`).
   - Filtered invalid `DOB` outliers (`1843-12-21`) and `deceased_indicator = 'Y'` records before computing age cohorts.
   - Isolated `19,821` approved orders (`99.11%` approval rate) and stripped currency formatting from `standard_cost` to compute net unit margin:
     $$\text{Gross Profit} = \text{list\_price} - \text{standard\_cost}$$
2. **Relational Star-Schema Join:** Inner-joined `Transactions` (`customer_id 1..3500`) to `CustomerDemographic` and `CustomerAddress` (noting `customer_id 5034` as an out-of-range test key in raw transactions) to profile margin contribution by `brand`, `product_line`, `wealth_segment`, and `state`.

## Key Quantitative Findings

### 1. Brand & Product-Line Gross Margin Concentration (`19,821` Approved Orders)

| Brand | Approved Orders ($n$) | Gross Revenue (\$ AUD) | Gross Profit (\$ AUD) | Gross Margin (%) | Share of Total Profit (%) |
|---|---:|---:|---:|---:|---:|
| **WeareA2B** | 3,265 | \$4,126,372.83 | **\$2,729,902.83** | **66.16%** | **25.20%** |
| **Solex** | 4,211 | **\$4,446,888.35** | **\$2,388,554.84** | 53.71% | 22.05% |
| **Trek Bicycles** | 2,965 | \$3,512,223.81 | \$1,822,846.19 | 51.90% | 16.83% |
| **Giant Bicycles** | 3,283 | \$4,055,613.05 | \$1,560,130.48 | 38.47% | 14.40% |
| **OHM Cycles** | 3,016 | \$2,965,459.80 | \$1,471,181.17 | 49.61% | 13.58% |
| **Norco Bicycles** | 2,885 | \$2,632,937.45 | \$858,888.52 | **32.62%** | 7.93% |
| **Total (Approved)** | **19,821** | **\$21,954,196.69** | **\$10,831,504.03** | **49.34%** | **100.00%** |

- **Margin vs Volume leader:** While `Solex` leads transaction volume (`4,211` orders) and top-line revenue (`\$4.45M`), **`WeareA2B` generates the highest total profit (\$2.73M, 25.20% of company margin)** thanks to a **66.16% gross margin**—more than double `Norco Bicycles` (`32.62%` gross margin).
- **Product-line dominance:** The `Standard` product line accounts for **74.45% of total company profit** (`\$8,063,637.59` across `14,048` orders), followed by `Road` (`\$1,388,338.93`, `3,932` orders), `Touring` (`\$1,339,014.55`, `1,225` orders at an exceptional **67.48% gross margin**), and `Mountain` (`\$40,512.96`, `420` orders).

### 2. Customer Wealth Segment & Geographic Profit Distribution

| Dimension | Segment | Approved Orders ($n$) | Gross Profit (\$ AUD) | Share of Profit (%) |
|---|---|---:|---:|---:|
| **Wealth Segment** | **Mass Customer** | 9,962 | **\$5,433,254.16** | **50.16%** |
| **Wealth Segment** | **High Net Worth** | 5,049 | \$2,747,307.74 | 25.37% |
| **Wealth Segment** | **Affluent Customer** | 4,807 | \$2,650,672.65 | 24.47% |
| **State** | **New South Wales (NSW)** | 10,587 | **\$5,736,612.99** | **53.04%** |
| **State** | **Victoria (VIC)** | 4,975 | \$2,756,536.71 | 25.49% |
| **State** | **Queensland (QLD)** | 4,228 | \$2,322,700.66 | 21.47% |

- **Mass-market scale:** `Mass Customer` accounts generate **50.16% of total gross profit (\$5.43M)**—nearly equal to `High Net Worth` (`\$2.75M`) and `Affluent` (`\$2.65M`) combined.
- **NSW geographic anchor:** **53.04% of total profit (\$5.74M)** originates in New South Wales (`10,587` orders), followed by Victoria (`\$2.76M`, `25.49%`) and Queensland (`\$2.32M`, `21.47%`).

## Executive Recommendations

1. **Prioritize `Mass Customer` + `NSW/VIC` Ages 30–49 in the 1,000-Lead Acquisition List:** Filter [`NewCustomerList.csv`](KPMG%20Data%20Analytics%20(Relational%20Database)/KPMG_Dataset/NewCustomerList.csv) for `Mass Customer` and `High Net Worth` households in `NSW` and `VIC` with high past-3-year cycling purchase frequency, bundling `WeareA2B` (`66.16%` margin) and `Touring` (`67.48%` margin) SKUs.
2. **Enforce Database Constraints on Ingestion:** Add foreign-key constraints (`Transactions.customer_id REFERENCES CustomerDemographic(customer_id)`), enum check constraints on `state` (`NSW`, `VIC`, `QLD`) and `gender`, and date-range validation (`DOB >= '1925-01-01'`) to eliminate ETL reconciliation overhead.

## How to Open / Run

- **Python / Jupyter:** Open [`Kpmg python Data Analytics.ipynb`](KPMG%20Data%20Analytics%20(Relational%20Database)/Kpmg%20python%20Data%20Analytics.ipynb) or [`Customer Retention EDA.ipynb`](Customer%20Retention%20Analysis/Customer%20Retention%20EDA.ipynb).
- **R / RStudio:** Render [`KPMG_Analysis(R).Rmd`](KPMG%20Data%20Analytics%20(Relational%20Database)/KPMG_Analysis(R).Rmd) or view [`Churn-EDA-R-.html`](Customer%20Retention%20Analysis/Churn-EDA-R-.html).
- **Power BI / Tableau:** Open [`KPMG Dashboard.pbix`](KPMG%20Data%20Analytics%20(Relational%20Database)/KPMG%20Dashboard.pbix) or [`Example dashboard2.twbx`](KPMG%20Data%20Analytics%20(Relational%20Database)/KPMG_VI_Model_Works/Example%20dashboard2.twbx).

## Post kit

- [`POST_LINKEDIN.md`](POST_LINKEDIN.md) — Case study on why data quality auditing precedes customer LTV modeling (`\$21.95M` revenue, `\$10.83M` profit).
- [`POST_X.md`](POST_X.md) — 6-tweet breakdown of brand margin economics and relational schema fixes.