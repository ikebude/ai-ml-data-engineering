1/6 What happens when you audit 20,000 retail transactions ($21.95M revenue, $10.83M gross profit) across 4,000 customers before launching a 1,000-lead acquisition campaign?

Here is the relational BI breakdown from my KPMG & PwC analytics suite. 🧵👇

2/6 Step 1 — Relational Schema Hygiene:
Raw customer tables had inconsistent state labels (`New South Wales` vs `NSW`, `Victoria` vs `VIC`), unparsed cost strings, an 1843 birth year outlier, and an out-of-range `customer_id = 5034` in `Transactions.csv`. Cleaning these preserved 19,821 approved orders (99.11%).

3/6 Step 2 — Brand Gross Margin Economics ($10.83M total profit):
• WeareA2B: $2.73M profit on $4.13M rev (66.16% gross margin — #1 profit contributor)
• Solex: $2.39M profit on $4.45M rev (53.71% margin — #1 volume)
• Trek: $1.82M profit (51.90% margin)
• Norco: $0.86M profit (32.62% margin).

4/6 Step 3 — Product Line Profit Share:
• Standard Line: 14,048 orders → $8.06M profit (74.45% of total profit)
• Road Line: 3,932 orders → $1.39M profit
• Touring Line: 1,225 orders → $1.34M profit (highest margin rate at 67.48%)
• Mountain Line: 420 orders → $40.5k profit.

5/6 Step 4 — Customer & Geographic Targeting:
• Mass Customers generate 50.16% of total gross profit ($5.43M), vs 25.37% High Net Worth ($2.75M) and 24.47% Affluent ($2.65M).
• New South Wales (NSW) drives 53.04% of profit ($5.74M), Victoria 25.49% ($2.76M), and Queensland 21.47% ($2.32M).

6/6 Full Python notebooks, R Markdown scripts, Tableau `.twbx`, and Power BI `.pbix` dashboards are in `analytics-and-bi/bi-analytics`.
