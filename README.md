# AI, ML & Data Engineering — Portfolio Hub

**Precious Ikebude** — **BI Scientist building AI/ML systems**  
*BI · Data Science · Machine Learning · LLM Apps · MLOps · Data Engineering*

This repository is the central hub for my applied machine-learning, business-intelligence, and data-engineering work:
- **Personal AI/ML products** I architected, trained, tested, and shipped end to end (`products/`),
- **Industry case studies** from commercial platforms I helped build at **3Consulting Limited** (`industry-work/`),
- **Machine learning & predictive modelling pipelines** (`machine-learning/`), and
- **Analytics, SQL & Power BI systems** (`analytics-and-bi/`), imported with full Git history.

---

## 📑 LinkedIn Case Study Carousels (PDF Downloads)

Each of the 9 platforms has a dedicated 6-slide executive case study carousel (16:9 widescreen, verified metrics, system architecture, and production UI mockups):

### 🏢 3Consulting Limited (Enterprise Solutions)
- [**SafeData Case Study Carousel (PDF)**](showcase/carousels/01-SafeData-Case-Study-Carousel.pdf) — Automated NDPA & GDPR Consent Disposal
- [**FraudGuard Case Study Carousel (PDF)**](showcase/carousels/02-FraudGuard-Case-Study-Carousel.pdf) — Sub-50ms Transaction Risk Engine & SAR Queue
- [**Africa Stablecoin Intelligence Case Study Carousel (PDF)**](showcase/carousels/03-Africa-Stablecoin-Intelligence-Case-Study-Carousel.pdf) — Pan-African FX Peg & Policy Matrix

### 🔬 Precious Ikebude (Personal AI & ML Products)
- [**Moniguard v2 Case Study Carousel (PDF)**](showcase/carousels/04-Moniguard-v2-Case-Study-Carousel.pdf) — Nigerian PoD Fraud Scoring Engine (PR-AUC 0.875)
- [**Lolo's Ledger Case Study Carousel (PDF)**](showcase/carousels/05-Lolos-Ledger-Case-Study-Carousel.pdf) — Multi-Asset Quant Risk & Tilt Detector (-19.6R tilt drag, synthetic benchmark)
- [**BI Operations Agent Case Study Carousel (PDF)**](showcase/carousels/06-BI-Operations-Agent-Case-Study-Carousel.pdf) — Governed Semantic Layer & AST Guarded SQL (96.0% in-sample, 56.0% held-out)
- [**LoanLens Case Study Carousel (PDF)**](showcase/carousels/07-LoanLens-Case-Study-Carousel.pdf) — Chronological Prosper Default Scorecard (ROC-AUC 0.705)
- [**Customer Intelligence Case Study Carousel (PDF)**](showcase/carousels/08-Customer-Intelligence-Case-Study-Carousel.pdf) — Calibrated Churn & Priority Call Queue
- [**AIOps Expense Tracker Case Study Carousel (PDF)**](showcase/carousels/09-AIOps-Expense-Tracker-Case-Study-Carousel.pdf) — NGN Expense NLP (0.9204 Macro-F1, synthetic data) & ETS Forecast

---

## 1. Personal AI & ML Products (`products/`)

| Product | One-Line Summary & Measured Results | Stack | Links |
|---|---|---|---|
| [**Moniguard**](products/moniguard/) | Real-time e-commerce & PoD fraud scoring (`0–1000` + reason codes). Calibrated XGBoost + Isolation Forest ensemble reaches **PR-AUC 0.875** (`95% CI: 0.841–0.898`), **Recall@5% alert rate = 0.895**, and **13.0 ms p95 scoring latency** on a 60k **synthetic** time-split benchmark. | Python, XGBoost, Scikit-learn, FastAPI, Airflow, MLflow, Docker | [Case Study](products/moniguard/) · [Product Repo](https://github.com/ikebude/MLOps-Fraud-Detection) |
| [**Lolo's Ledger**](products/lolos-ledger/) | Multi-asset trading journal, position-sizing risk engine, and educational AI performance coach. Full-stack NestJS + React + BullMQ monorepo built on the engine of my archived desktop predecessor (FXLedger v1.1.0): **363 core** (349 ported from FXLedger v1.1.0) **+ 155 API + 25 web + 7 Python tests** and **14 Playwright e2e runs** (7 tests × 2 viewports). | TypeScript, React, NestJS, PostgreSQL, Redis, Electron, Playwright | [Case Study](products/lolos-ledger/) · *Source private* |
| [**BI Operations Agent**](products/bi-operations-agent/) | Plain-English analytics agent that queries a read-only SQLite store through a governed YAML semantic layer and AST SQL guard, monitors daily KPIs, and writes weekly executive summaries. On **synthetic** retail data: **96.0% (48/50)** in-sample, **56.0% (14/25)** held-out, **12/12** adversarial prompts blocked, **36.6 ms p95**. | Python, FastAPI, SQLite, sqlglot, Streamlit | [Case Study](products/bi-operations-agent/) · [Product Repo](https://github.com/ikebude/AIMLOps-BI-Operations-Agent) |
| [**AIOps Expense Tracker**](products/expense-tracker/) | NGN-first personal & SME finance app with TF-IDF + Logistic Regression auto-categorisation retrained on user corrections (**0.9204 Macro-F1**), receipt-text parsing (no OCR), MAD anomaly detection (**F1 0.973**), and a 3-month ETS forecast (**8.1% holdout WAPE**), all on **synthetic** data. | Python, Scikit-learn, FastAPI, React, Vite | [Case Study](products/expense-tracker/) · [Product Repo](https://github.com/ikebude/AIOps_Expense_Tracker) |

---

## 2. Industry Case Studies — 3Consulting Limited (`industry-work/`)

> *Shown as engineering case studies (problem, architecture, my role, and planned public sites). Proprietary company source code is never published here.*

| Platform | Domain | What It Does & My Role | Case Study & Public Site |
|---|---|---|---|
| [**SafeData (ADRS)**](industry-work/safedata/) | Data Retention & Consent Governance | Tracks record retention schedules, processes consent-withdrawal webhooks into disposal countdowns, enforces legal holds/dual approvals, and seals SHA-256 audit trails. *Role: retention/consent lifecycle logic, PostgreSQL test suite, GitHub Actions CI & security scanning.* | [Case Study](industry-work/safedata/) · [safedata.3consult-ng.com](https://safedata.3consult-ng.com) *(deployment pending verification)* |
| [**FraudGuard**](industry-work/fraudguard/) | Real-Time Transaction Fraud Prevention | Multi-service fraud intelligence platform (PostgreSQL outbox → Kafka → streaming inference → Flask analyst queue + SAR/governance + Airflow/MLflow retraining). *Role: feature engineering, ensemble pipeline, Airflow/MLflow MLOps, analyst dashboard.* | [Case Study](industry-work/fraudguard/) · [fraudguard.3consult-ng.com](https://fraudguard.3consult-ng.com) *(deployment pending verification)* |
| [**Africa Stablecoin Intelligence (ASI)**](industry-work/africa-stablecoin-intelligence/) | Market & Regulatory Intelligence | Tracks African stablecoin adoption, corridor metrics, central-bank regulatory posture by country, and editorial research dispatches. *Role: data source schema, Light/Dark/System UI across public & admin apps, launch indexing.* | [Case Study](industry-work/africa-stablecoin-intelligence/) · [africastablecoinintelligence.com](https://africastablecoinintelligence.com) *(deployment pending verification)* |

---

## 3. Machine Learning Projects (`machine-learning/`)

| Project | Focus | Folder |
|---|---|---|
| **Waze User Churn Prediction** | Behavioural churn classification, feature engineering (session velocity, streak ratios), and retention targeting | [`machine-learning/waze-churn-prediction/`](machine-learning/waze-churn-prediction/) |
| **TLC CabFare Intelligence (NYC Taxi)** | Fare modelling and demand/anomaly analysis across NYC Yellow Taxi trip records | [`machine-learning/tlc-cab-fare-intelligence/`](machine-learning/tlc-cab-fare-intelligence/) |
| **Customer Retention & Churn Analysis** | Cohort retention, churn driver identification, and segment risk profiling (foundation for **Customer Intelligence**) | [`machine-learning/customer-retention/`](machine-learning/customer-retention/) |
| **Prosper Loan Credit Risk Analysis** | Borrower default risk, credit-grade behaviour, and yield vs. loss analysis across 113,937 Prosper listings (55,518 closed loans modelled) (foundation for **LoanLens**) | [`machine-learning/prosper-loan-risk/`](machine-learning/prosper-loan-risk/) |
| **S&P 500 Financial Clustering & EDA** | SQL normalization + PCA dimensionality reduction + K-Means market segmentation across S&P 500 companies | [`machine-learning/sp500-analysis/`](machine-learning/sp500-analysis/) |
| **Cars Model Analysis** | Multi-language (Python, R, Power BI) pricing and feature analysis | [`machine-learning/cars-model-analysis/`](machine-learning/cars-model-analysis/) |

---

## 4. Analytics, BI & SQL Projects (`analytics-and-bi/`)

| Project | Focus | Folder |
|---|---|---|
| **CRM Sales Funnel Analysis** | B2B pipeline conversion rates, stage drop-off diagnostics, and deal velocity | [`analytics-and-bi/crm-sales-analysis/`](analytics-and-bi/crm-sales-analysis/) |
| **Power BI Dashboard Portfolio** | Executive dashboards using DAX time intelligence, data modelling, and drill-through views | [`analytics-and-bi/power-bi-dashboards/`](analytics-and-bi/power-bi-dashboards/) |
| **Strategic SQL Querying** | Complex MS SQL Server queries (CTEs, window functions, multi-table joins) for operational decision-making | [`analytics-and-bi/sql-querying/`](analytics-and-bi/sql-querying/) |
| **BI Analytics Simulations** | End-to-end client data quality, segmentation, and executive reporting packages | [`analytics-and-bi/bi-analytics/`](analytics-and-bi/bi-analytics/) |
| **Global Data Analytics Projects** | Exploratory data analysis and statistical reporting in Python and R | [`analytics-and-bi/global-data-analytics/`](analytics-and-bi/global-data-analytics/) |

---

## 5. Ground Rules This Repository Follows

1. **Real numbers only.** Every metric reported comes from executing the code in the repository. No invented accuracy or synthetic business claims (Moniguard and other product metrics are on synthetic data where stated).
2. **The right metric for imbalanced problems.** Fraud, churn, and loan default models report **PR-AUC**, **Recall at a fixed alert/contact budget**, **Precision**, and **95% bootstrap confidence intervals**—never raw accuracy alone.
3. **Strict confidentiality.** Consulting case studies in `industry-work/` document problem framing, architecture, and my engineering contributions—never client or employer source code.
4. **Automated CI verification.** [`.github/workflows/ci.yml`](.github/workflows/ci.yml) discovers and runs tests across ML/product folders on every push.

---

## Connect

- **GitHub:** [github.com/ikebude](https://github.com/ikebude)
- **Portfolio:** [datascienceportfol.io/ikebude](https://www.datascienceportfol.io/ikebude)
- **Email:** [precious.ikebude@outlook.com](mailto:precious.ikebude@outlook.com)
