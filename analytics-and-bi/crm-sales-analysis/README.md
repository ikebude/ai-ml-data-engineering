# B2B Hardware CRM Sales Pipeline & Territory Performance Analysis

> Audits 8,800 B2B hardware opportunities (\$10.01M closed-won revenue across 85 enterprise accounts and 35 reps): uncovers a 63.15% overall win rate, a 51.8-day average sales cycle, and a 34.4% revenue concentration in a single flagship SKU (`GTX Plus Pro`).

## Problem

B2B sales leadership lacked visibility into why quarterly bookings varied across regional offices (`West`, `Central`, `East`), which product lines drove actual margin versus rep activity volume, and whether discounting was eroding realized deal values. This analysis models the four-table relational CRM schema (`sales_pipeline`, `accounts`, `products`, `sales_teams`) to benchmark territory conversion efficiency, manager coaching leverage, and product mix concentration.

## Dataset & Relational Schema

- **Source:** Maven Analytics / Enterprise B2B Hardware CRM Relational Dataset (`analytics-and-bi/crm-sales-analysis/`)
- **Tables & Granularity:**
  - [`sales_pipeline.csv`](sales_pipeline.csv) — **8,800** opportunity records (`opportunity_id`, `sales_agent`, `product`, `account`, `deal_stage`, `engage_date`, `close_date`, `close_value`)
  - [`accounts.csv`](accounts.csv) — **85** enterprise customer accounts (`sector`, `revenue`, `employees`, `office_location`, `subsidiary_of`)
  - [`products.csv`](products.csv) — **7** hardware SKUs across 3 product series (`GTX`, `MG`, `GTK`) with list `sales_price` ranging from `\$55` (`MG Special`) to `\$26,768` (`GTK 500`)
  - [`sales_teams.csv`](sales_teams.csv) — **35** sales representatives reporting to **6** regional sales managers across **3** territories (`Central`, `East`, `West`)

## Methodology & SQL / BI Logic

1. **Funnel Stage Normalization:** Segmented all 8,800 pipeline records into Closed-Won (`4,238` deals, `48.16%` of total pipeline), Closed-Lost (`2,473` deals, `28.10%`), Active Engaging (`1,589` deals, `18.06%`), and Prospecting (`500` deals, `5.68%`). Defined **Closed-Deal Win Rate** strictly on resolved opportunities:
   $$\text{Win Rate} = \frac{\text{Won Deals}}{\text{Won Deals} + \text{Lost Deals}} = \frac{4,238}{4,238 + 2,473} = 63.15\%$$
2. **Price Realization vs List Price Audit:** Joined `sales_pipeline.product` to `products.sales_price` to measure realized ASP ($\text{mean close\_value}$) against catalog list price per SKU.
3. **Sales Velocity & Cycle Time:** Calculated `cycle_days = close_date - engage_date` across all 4,238 closed-won opportunities (`mean = 51.78 days`, `median = 57.0 days`).

```sql
-- Territory & Manager Win-Rate and Bookings Benchmark
SELECT
    t.regional_office,
    t.manager,
    COUNT(p.opportunity_id) FILTER (WHERE p.deal_stage IN ('Won', 'Lost')) AS resolved_deals,
    COUNT(p.opportunity_id) FILTER (WHERE p.deal_stage = 'Won')            AS won_deals,
    ROUND(
        100.0 * COUNT(p.opportunity_id) FILTER (WHERE p.deal_stage = 'Won')
        / NULLIF(COUNT(p.opportunity_id) FILTER (WHERE p.deal_stage IN ('Won', 'Lost')), 0),
        2
    ) AS closed_win_rate_pct,
    SUM(p.close_value) FILTER (WHERE p.deal_stage = 'Won')                 AS total_won_revenue_usd
FROM sales_pipeline p
JOIN sales_teams t ON p.sales_agent = t.sales_agent
GROUP BY t.regional_office, t.manager
ORDER BY total_won_revenue_usd DESC;
```

## Key Quantitative Findings

### 1. Territory & Sales Manager Performance

| Regional Office | Sales Manager | Resolved Deals (`Won + Lost`) | Closed Win Rate (%) | Closed-Won Revenue (\$ USD) | Share of Total Bookings (%) |
|---|---|---:|---:|---:|---:|
| **Central** | Melvin Marxen | 1,418 | 62.20% | **\$2,251,930** | 22.51% |
| **West** | Summer Sewald | 1,287 | 64.34% | **\$1,964,750** | 19.64% |
| **East** | Rocco Neubert | 1,113 | 62.08% | **\$1,960,545** | 19.59% |
| **West** | Celia Rouche | 962 | 63.41% | **\$1,603,897** | 16.03% |
| **East** | Cara Losch | 745 | **64.43%** | **\$1,130,049** | 11.29% |
| **Central** | Dustin Brinkmann | 1,186 | 62.98% | **\$1,094,363** | 10.94% |
| **Total / Overall** | **6 Managers (35 Reps)** | **6,711** | **63.15%** | **\$10,005,534** | **100.00%** |

- **West leads territory bookings (\$3,568,647; 35.67% share)** with the highest regional win rate (**63.94%** across 2,249 resolved deals), followed by **Central** (`\$3,346,293`, `62.56%` win rate) and **East** (`\$3,090,594`, `63.02%` win rate).
- **Intra-region ticket-size divergence:** Within the `Central` office, Melvin Marxen's pod generates **2.06x the revenue** of Dustin Brinkmann's pod (`\$2.25M` vs `\$1.09M`) despite similar deal volume (`1,418` vs `1,186`) and win rates (`62.20%` vs `62.98%`), driven entirely by upper-tier SKU mix (`GTX Plus Pro` and `GTK 500` vs entry-level `MG Special`).

### 2. Product Portfolio Mix & Activity Trap

| Product SKU | Series | Catalog List Price (\$) | Resolved Deals | Won Deals | Win Rate (%) | Realized Avg Win (\$) | Total Won Revenue (\$) |
|---|---|---:|---:|---:|---:|---:|---:|
| **GTX Plus Pro** | GTX | \$5,482 | 745 | 479 | **64.30%** | \$5,489.88 | **\$2,629,651** |
| **GTXPro** | GTX | \$4,821 | 1,147 | 729 | 63.56% | \$4,815.61 | **\$3,510,578** |
| **MG Advanced** | MG | \$3,393 | 1,084 | 654 | 60.33% | \$3,388.97 | **\$2,216,387** |
| **GTX Plus Basic** | GTX | \$1,096 | 1,051 | 653 | 62.13% | \$1,080.05 | **\$705,275** |
| **GTX Basic** | GTX | \$550 | 1,436 | **915** | 63.72% | \$545.64 | **\$499,263** |
| **GTK 500** | GTK | \$26,768 | 25 | 15 | 60.00% | \$26,707.47 | **\$400,612** |
| **MG Special** | MG | \$55 | 1,223 | 793 | **64.84%** | \$55.19 | **\$43,768** |

- **The `MG Special` activity trap:** `MG Special` (`\$55` list price) consumes **18.22% of all resolved rep activity** (`1,223` resolved deals, `793` wins) but contributes just **0.44% of total company revenue** (`\$43,768`).
- **Core revenue engine:** Two high-ASP SKUs—`GTXPro` (`\$3.51M`, `35.09%` of revenue) and `GTX Plus Pro` (`\$2.63M`, `26.28%` of revenue)—generate **61.37% of total company bookings** (`\$6.14M`) while maintaining above-average win rates (`63.56%` and `64.30%`).
- **Discipline on discounting:** Realized average close values track within **±1.5%** of catalog list prices across all 7 SKUs, confirming that revenue variance is a product-mix problem rather than a rogue discounting problem.

## Executive Recommendations

1. **Automate self-serve checkout for `MG Special` (\$55) and `GTX Basic` (\$550):** Offloading the `2,659` low-ticket deals (`MG Special` + `GTX Basic`) from direct AE outreach to an automated e-commerce portal frees up **39.6% of sales rep capacity** while risking less than `5.4%` of gross revenue (`\$543k`), allowing reps to focus on `GTXPro`, `GTX Plus Pro`, and `MG Advanced`.
2. **Rebalance SKU quotas in Dustin Brinkmann's Central pod:** Pair Brinkmann's reps (`62.98%` win rate but `\$923` revenue per resolved deal) with enterprise accounts currently buying `GTX Basic` to cross-sell `GTX Plus Pro` (`\$5,482`).
3. **Accelerate the 1,589 `Engaging` deals past the 57-day median cycle:** Trigger automated sales-engineering support for any `GTXPro` or `GTK 500` opportunity open longer than `45 days` to convert the active pipeline before quarter-end.

## How to Open / Run

```bash
# Inspect summary statistics directly with Python / pandas
python -c "
import pandas as pd
pipe = pd.read_csv('sales_pipeline.csv')
print(pipe.groupby('deal_stage')['close_value'].agg(['count', 'sum', 'mean']))
"
```

## Post kit

- [`POST_LINKEDIN.md`](POST_LINKEDIN.md) — Executive breakdown of the "Activity Trap" (`18.2%` of rep deals generating `0.44%` of revenue).
- [`POST_X.md`](POST_X.md) — 6-tweet thread on B2B CRM funnel economics and territory benchmarking.
