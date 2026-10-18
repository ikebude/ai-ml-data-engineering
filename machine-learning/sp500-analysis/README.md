# 📊 Exploratory Data Analysis of S&P 500 Companies

## 🧠 Background Information

The S&P 500 index represents the performance of 500 of the largest companies listed on U.S. stock exchanges. These companies span across major sectors of the U.S. economy and provide a comprehensive snapshot of corporate America’s financial health and market behavior.

Understanding the composition, financial metrics, and industry representation of these companies is essential for investors, analysts, and business strategists alike.

## 🎯 Project Objectives

The objective of this project is to perform an Exploratory Data Analysis (EDA) on a dataset containing information on S&P 500 companies. The goals include:

- Understanding the distribution of companies across sectors and industries.
- Analyzing key financial metrics such as market capitalization, EBITDA, revenue growth, and stock prices.
- Exploring geographical distributions of company headquarters.
- Identifying standout companies and patterns in growth, profitability, and employee size.
- Preparing insights that can inform investment decisions or further financial modeling.
- **Data Source**: Manually compiled CSV of S&P 500 companies including financial metrics and metadata.
- **Tools Used**:  
  - SQL (MS SQL Server): Data cleaning and preparation  
  - Python (Pandas, Seaborn, Scikit-learn, Matplotlib): Analysis & Visualization  
  - Jupyter Notebooks: Documentation and interactivity

## 📁 Data Description

The dataset (`sp500_companies.xlsx`) consists of 502 rows and 16 columns, with each row representing a publicly listed company. Below are the columns in the dataset:

| Column Name           | Description |
|-----------------------|-------------|
| `Exchange`            | Stock exchange the company is listed on |
| `Symbol`              | Stock ticker symbol |
| `Shortname`           | Short name of the company |
| `Longname`            | Full legal name of the company |
| `Sector`              | Sector of operation |
| `Industry`            | Specific industry classification |
| `Currentprice`        | Latest trading price |
| `Marketcap`           | Market capitalization (in USD) |
| `Ebitda`              | Earnings before interest, tax, depreciation, and amortization |
| `Revenuegrowth`       | Year-over-year revenue growth rate |
| `City`, `State`, `Country` | Location of company headquarters |
| `Fulltimeemployees`   | Number of full-time employees |
| `Longbusinesssummary` | Brief company profile |
| `Weight`              | Weight of the company in the S&P 500 index |

## 🛠️ Deliverables

- A well-commented Jupyter Notebook containing:
  - Data cleaning and preparation
  - Univariate and bivariate visualizations
  - Summary statistics
  - Key observations
- Summary visualizations (bar charts, histograms, boxplots, etc.)
- This `README.md` file summarizing the project

## 🧰 Technologies & Libraries

| Tool/Language | Usage |
|---------------|-------|
| **SQL (T-SQL)** | Data loading, column cleanup, type conversions |
| **Pandas** | Data wrangling, feature engineering |
| **Matplotlib/Seaborn** | Visualizations |
| **Scikit-learn** | PCA & clustering |
| **Scipy** | Statistical analysis (Z-score for outliers) |

## 📌 Summary of Findings
Here’s a preview of what we aim to uncover:
- Top 10 companies by market capitalization
- Most represented sectors and industries
- Relationships between company size, revenue growth, and profitability
- Geographical concentrations of S&P 500 companies
- Noteworthy outliers or trends in financial performance

## 💡 Key Insights (To Be Prepared)
Key insights from the EDA include:
- **Sector Distribution**: Visualization of how companies are distributed across sectors
- **Top Companies by Market Cap & Employees**: Identification of dominant players
- **Revenue Growth vs. EBITDA**: Insights into profitability trends
- **Correlation Heatmap**: Relationships among financial features


## 🧪 Advanced Data Analysis

### 🔹 Feature Engineering

- **Price-to-EBITDA Ratio**
- **Employees per Market Cap**
- **Log-transformed Market Cap**

### 🔹 Outlier Detection

- Z-score based anomaly detection flags unusually large or small companies across financial metrics.

### 🔹 Sector Comparisons

- Visual analysis of average financial ratios across sectors gives clues on performance norms.

### 🔹 PCA & Clustering

- Dimensionality reduction reveals latent groupings among companies based on financial traits.
- Helps in understanding how companies cluster by financial behavior beyond sectors.

## 💼 Author

**Precious Chidiebere Ikebude**  
[GitHub](https://github.com/ikebude) | [Portfolio](https://www.datascienceportfol.io/ikebude) | [Upwork Profile](https://www.upwork.com/freelancers/~017b5ef2fbb723606e)

A BI Developer and Data Analyst passionate about business insights, predictive modeling, and automation.

---

## 🚀 Future Work

- Time-series analysis with quarterly financials  
- Integration with live APIs (e.g., Yahoo Finance or Alpha Vantage)  
- Deployment of an interactive dashboard using Streamlit or Power BI

## 📌 License

This project is open-source and available under the MIT License.

---

📌 **Note**: All analysis is done using Python in a Jupyter Notebook, using libraries such as `pandas`, `matplotlib`, `seaborn`, and `plotly`.
