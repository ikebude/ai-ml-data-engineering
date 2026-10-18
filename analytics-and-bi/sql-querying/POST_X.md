1/6 How do you evaluate a restaurant loyalty program and promotional points ledger purely in PostgreSQL?

Here is a walkthrough of 10 analytical SQL patterns (CTEs, `RANK() OVER`, temporal joins, and `CASE` multipliers) from `analytics-and-bi/sql-querying`. 🧵👇

2/6 The Schema (`dannys_diner`):
• `sales`: 15 orders across Customers A, B, and C (Jan–Feb 2021)
• `menu`: Sushi ($10), Curry ($15), Ramen ($12)
• `members`: Customer A (joined 2021-01-07), Customer B (joined 2021-01-09), Customer C (non-member).

3/6 Spend & Visit Frequency (Q1–Q2):
• Customer A: $76 spent across 4 visit days (6 items)
• Customer B: $74 spent across 6 visit days (6 items)
• Customer C: $36 spent across 2 visit days (3 items)
Total revenue = $186. Loyalty members average $75.00 vs $36.00 for non-members (2.08x).

4/6 Menu Economics & Window Functions (`RANK() OVER (PARTITION BY customer_id)` Q3–Q5):
• Ramen ($12) is the #1 item with 8 orders ($96 = 51.61% of total revenue), followed by Curry (4 orders, $60) and Sushi (3 orders, $30).
• Curry & Sushi act as Day-1 acquisition hooks, while Ramen drives repeat retention.

5/6 Pre- vs Post-Membership Temporal Split (Q6–Q8):
• Before joining (`order_date < join_date`), Customer A spent $25 (2 items) and Customer B spent $40 (3 items).
• After joining (`order_date >= join_date`), Customer A spent $51 (4 items — a 2.04x jump), triggered immediately by ordering Curry on join day (`2021-01-07`) followed by 3 Ramen orders.

6/6 Promotional Points Ledger (`CASE WHEN` Q9–Q10):
• Base rule (10 pts/$1, 2x on Sushi): B leads with 940 pts, A has 860 pts, C has 360 pts.
• Adding the 2x first-week enrollment promo boosts A's January balance to 1,370 pts.
Full SQL script in `analytics-and-bi/sql-querying/QUERYING DATA WITH SQL.sql`.
