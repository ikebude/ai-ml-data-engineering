Clean SQL isn't just about getting the query to run—it's about turning raw transaction logs into unit-economics decisions on customer loyalty and product mix.

In my PostgreSQL case study on Danny's Diner (`dannys_diner` schema: `sales`, `menu`, `members`), I used Common Table Expressions (CTEs), partitioned `RANK()` window functions, and temporal `join_date` filters to audit loyalty program performance:

1. **2.08x Loyalty Spend Lift:** Enrolled loyalty members (`Customer A` at **\$76** across 4 visit days and `Customer B` at **\$74** across 6 visit days) averaged **\$75.00** in spend versus **\$36.00** (2 visit days) for non-member `Customer C`. For `Customer A`, spend more than doubled from **\$25 pre-membership** to **\$51 post-membership**.
2. **Menu Concentration (`53.3%` Ramen Share):** `Ramen` (`\$12`) accounted for **8 of the 15 total orders** (**\$96**, or **51.61% of total \$186 revenue**), outperforming `Curry` (`4` orders, `\$60`) and `Sushi` (`3` orders, `\$30`).
3. **Promotional Points Liability Modeling:** Using conditional `CASE WHEN` date-window rules, introducing a 7-day 2x enrollment bonus boosted `Customer A`'s January loyalty balance from **860 base points to 1,370 points** (`+59.3%`), creating a strong incentive for immediate post-signup repeat visits.

What is your go-to SQL window pattern for isolating pre- vs post-onboarding customer behavior?

#SQL #PostgreSQL #DataAnalytics #BusinessIntelligence #CustomerLoyalty
