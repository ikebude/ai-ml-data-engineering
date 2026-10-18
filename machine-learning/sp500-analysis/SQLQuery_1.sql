/*
**<u>Introduction</u>**

This project analyzes the S&P 500 companies using SQL for data processing and Power BI for visualization. The goal is to uncover market trends, sector distributions, and financial insights.
*/

use chidiszn; -- the database name.



SELECT TOP (10) [Exchange]

      ,[Symbol]

      ,[Shortname]

      ,[Longname]

      ,[Sector]

      ,[Industry]

      ,[Currentprice]

      ,[Marketcap]

      ,[Ebitda]

      ,[Revenuegrowth]

      ,[City]

      ,[State]

      ,[Country]

      ,[Fulltimeemployees]

      ,[Longbusinesssummary]

      ,[Weight] AS sp500_companies_cleaned

  FROM [chidiszn].[dbo].[sp500_companies] -- Lets look at the data.







/*
### **<u>Data Cleaning Steps</u>**

- Handled missing values
    
- Ensured correct data types
    
- Standardized column names (optional for SQL use)
    

Then I wrote an SQL script assuming this data is in a table named `sp500_companies`.

  

**<u>Data Processing & Queries</u>**
*/

SELECT COUNT(*) FROM sp500_companies; -- Total companies

/*
The total number of S&P 500 companies were 502 on the dataset collected for analysis.
*/

SELECT DISTINCT sector FROM sp500_companies; -- List of sectors

/*
The code above shows the sectors each companies falls under.
*/

SELECT sector, AVG(revenuegrowth) AS avg_growth

FROM sp500_companies

GROUP BY sector

ORDER BY avg_growth DESC;

/*
From Basic analysis, we can see that Financial Services lies as the biggest sector using Average groth rate.
*/

SELECT SecSta = state, COUNT(*) AS company_count FROM sp500_companies GROUP BY state ORDER BY company_count DESC;

/*
**Company Distribution by State**
*/

SELECT sector, COUNT(*) AS company_count

FROM sp500_companies

GROUP BY sector

ORDER BY company_count DESC;

/*
**<u>Sector distribution</u>**
*/

/*
We've done data cleaning and descriptive analysis. Now we create a python scriptfor the data analysis.
*/

