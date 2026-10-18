# Relational Loyalty & Customer Analytics in PostgreSQL (Danny's Diner Case Study)

> Solves 10 restaurant loyalty and unit-economics questions on a 3-table PostgreSQL relational schema (`sales`, `menu`, `members`) using Common Table Expressions (CTEs), `RANK() OVER (PARTITION BY ...)` window functions, temporal join-date filtering, and conditional `CASE` reward-point multipliers.

## Problem

Danny's Diner (Case Study #1 from Danny Ma's 8-Week SQL Challenge) needed to evaluate whether its fledgling customer loyalty program (`members`) drove higher post-enrollment spend, which menu items acted as first-touch acquisition hooks versus repeat-purchase anchors, and how a promotional 2x first-week points multiplier impacted reward liabilities by the end of January 2021.

## Dataset & PostgreSQL Schema

Defined in [`QUERYING DATA WITH SQL.sql`](QUERYING%20DATA%20WITH%20SQL.sql) (`CREATE SCHEMA dannys_diner`):
- **`dannys_diner.sales` (`15` transaction rows):** `customer_id` (`A`, `B`, `C`), `order_date` (`2021-01-01` to `2021-02-01`), `product_id` (`1..3`).
- **`dannys_diner.menu` (`3` SKUs):**
  - `product_id = 1`: `sushi` (`\$10`)
  - `product_id = 2`: `curry` (`\$15`)
  - `product_id = 3`: `ramen` (`\$12`)
- **`dannys_diner.members` (`2` enrolled loyalty members):**
  - `customer_id = 'A'`: `join_date = 2021-01-07`
  - `customer_id = 'B'`: `join_date = 2021-01-09`
  - (`customer_id = 'C'` remains a non-member control cohort).

## Methodology & Advanced SQL Patterns

All 10 analytical queries in [`QUERYING DATA WITH SQL.sql`](QUERYING%20DATA%20WITH%20SQL.sql) are written in PostgreSQL using:
1. **Window Functions (`RANK() OVER (PARTITION BY customer_id ORDER BY ...)`):** Used to isolate each customer's first-ever order (Q3), most frequently ordered item (Q5), first post-membership purchase (Q6), and final pre-membership purchase (Q7) while preserving ties.
2. **Temporal Pre/Post Loyalty Segmentation:** Filtered `s.order_date < mb.join_date` versus `s.order_date >= mb.join_date` to measure pre-membership baseline spend (Q8) versus post-enrollment expansion.
3. **Conditional Points Ledger (`CASE WHEN ... END`):** Modeled both the base loyalty rule (`10 pts/\$1`, `2x` multiplier on `sushi` $\rightarrow$ `20 pts/\$1` in Q9) and the promotional launch rule (`2x` multiplier on **all items** during `join_date` through `join_date + 6 days` in Q10).

```sql
-- Q10: Promotional First-Week 2x Points + Sushi 2x Multiplier Ledger (January Cohort)
WITH points_ledger AS (
    SELECT
        s.customer_id,
        s.order_date,
        m.product_name,
        m.price,
        CASE
            WHEN s.order_date BETWEEN mb.join_date AND (mb.join_date + INTERVAL '6 days') THEN m.price * 20
            WHEN m.product_name = 'sushi' THEN m.price * 20
            ELSE m.price * 10
        END AS order_points
    FROM dannys_diner.sales s
    JOIN dannys_diner.menu m    ON s.product_id = m.product_id
    JOIN dannys_diner.members mb ON s.customer_id = mb.customer_id
    WHERE s.order_date <= '2021-01-31'
)
SELECT customer_id, SUM(price) AS jan_spend_usd, SUM(order_points) AS total_jan_points
FROM points_ledger
GROUP BY customer_id
ORDER BY customer_id;
```

## Key Quantitative Findings (Verified from `QUERYING DATA WITH SQL.sql`)

### 1. Customer Spend, Visit Frequency & Loyalty Lift

| Customer ID | Loyalty Status (`join_date`) | Distinct Visit Days | Total Items Ordered | Pre-Member Spend (\$) | Post-Member Spend (\$) | Total Spend (\$) | Base Points (Q9) | Launch Promo Points (Q10, Jan) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Customer A** | Member (`2021-01-07`) | 4 days | 6 items | \$25 (2 items) | **\$51** (4 items) | **\$76** | 860 pts | **1,370 pts** |
| **Customer B** | Member (`2021-01-09`) | **6 days** | 6 items | \$40 (3 items) | **\$34** (3 items) | **\$74** | **940 pts** | 820 pts (Jan) |
| **Customer C** | Non-Member (`NULL`) | 2 days | 3 items | \$36 (3 items) | \$0 | **\$36** | 360 pts | — |
| **Total** | **2 Members / 1 Non-Member** | **12 customer-days** | **15 items** | **\$101** | **\$85** | **\$186** | **2,160 pts** | — |

- **Loyalty members spend 2.08x more than non-members:** Enrolled members `A` (`\$76`) and `B` (`\$74`) average **\$75.00 in total spend** and **5.0 visit days**, compared to **\$36.00** and **2 visit days** for non-member `C`.
- **Post-enrollment spend acceleration for Customer A:** Prior to joining on `2021-01-07`, Customer A spent `\$25` across 2 items (`sushi` + `curry` on `Jan 1`). After joining, Customer A spent **\$51** across 4 items (`curry` on `Jan 7` + three `ramen` bowls on `Jan 10–11`)—a **2.04x post-membership spend increase**.

### 2. Menu SKU Economics & Ordering Behavior
- **Ramen is the #1 volume & revenue anchor (`53.3%` of all orders):** Across all 15 transactions (`\$186` total revenue), **`ramen` (\$12) was ordered 8 times (\$96; 51.61% of revenue)**, **`curry` (\$15) was ordered 4 times (\$60; 32.26% of revenue)**, and **`sushi` (\$10) was ordered 3 times (\$30; 16.13% of revenue)**.
- **Acquisition hook vs repeat habit:** First-day orders (`2021-01-01`) skewed toward `curry` (`A` and `B`) and `sushi` (`A`), whereas `ramen` was the #1 repeat favorite for `Customer A` (`3` orders), `Customer C` (`3` orders), and tied for #1 across `Customer B` (`2` orders each of `sushi`, `curry`, and `ramen`).

## Executive Recommendations

1. **Convert Non-Member Repeat Ramen Buyers (`Customer C` Profile) at Visit #2:** Non-member `Customer C` ordered `ramen` three times across two visits (`\$36` spend). Offering an instant 2x first-week points bonus at the second visit captures high-propensity repeat diners into the `members` table.
2. **Use `Sushi` (`2x` Points) as a Basket-Expander Add-On:** Because `sushi` (`\$10`) represents only `20%` of unit volume (`3/15` items) despite its permanent `2x` points multiplier, bundle a half-price `sushi` starter with `ramen` orders to raise average check size above `\$18`.

## How to Open / Run

```bash
# Execute the schema creation, seed inserts, and all 10 analytical queries in PostgreSQL
psql -U postgres -f "QUERYING DATA WITH SQL.sql"
```

## Post kit

- [`POST_LINKEDIN.md`](POST_LINKEDIN.md) — Breakdown of window functions (`RANK() OVER`) and loyalty program unit economics in SQL.
- [`POST_X.md`](POST_X.md) — 6-tweet walkthrough of the 10 SQL loyalty queries and exact findings.