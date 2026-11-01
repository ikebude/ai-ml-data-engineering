# AI, ML & Data Engineering Portfolio

**Precious Chidiebere Ikebude** · BI Scientist building AI/ML systems · Lagos, Nigeria

I turn business data into dashboards, models and small production-style services. I have 3+ years of data, BI and finance-analytics work (since Nov 2022), and I am currently BI Scientist / AI/ML Engineer at 3Consulting Limited (Junior Data Analyst there from Jun 2025, promoted Nov 2025).

**Open to:** BI Analyst, Data Analyst, Data Scientist and junior ML Engineer roles. Remote (Nigeria or worldwide), full-time or contract.
**Contact:** [precious.ikebude@outlook.com](mailto:precious.ikebude@outlook.com) · [WhatsApp +234 813 678 7181](https://wa.me/2348136787181) · [ikebude.github.io](https://ikebude.github.io) · [github.com/ikebude](https://github.com/ikebude)

---

## Start here: three projects

| Project | What it shows | Result (from the repo's `reports/*.json`) |
|---|---|---|
| [**Moniguard**](products/moniguard/) · fraud scoring service | ML engineering end to end: feature pipeline shared by training and serving, calibrated XGBoost + Isolation Forest, FastAPI, MLflow, Airflow, Docker | PR-AUC **0.959** (95% CI 0.942–0.972) in batch evaluation and **0.837** scored one transaction at a time through the API, on 60,000 **synthetic** transactions with a time-based split |
| [**LoanLens**](machine-learning/prosper-loan-risk/) · credit default scorecard | Careful data science: leakage gate in tests, out-of-time split, calibration, a policy simulator and its limits | Out-of-time ROC-AUC **0.705** (95% CI 0.695–0.714), KS **0.303** on 13,880 later Prosper loans (public data) |
| [**BI Operations Agent**](products/bi-operations-agent/) · plain-English analytics | BI plus LLM tooling: governed semantic layer, read-only SQL guard, KPI anomaly monitor | **96.0%** (48/50) in-sample and **56.0%** (14/25) held-out questions answered correctly, **12/12** unsafe prompts blocked, 36.6 ms p95, on **synthetic** retail data |

**Stack:** Python (pandas, scikit-learn, XGBoost), SQL (PostgreSQL, SQL Server, SQLite), Power BI (DAX), Tableau, R, FastAPI, MLflow, Airflow, Docker, GitHub Actions; TypeScript/React for product front ends.

---

## 1. Personal products (`products/`)

| Product | Summary and measured results | Stack | Links |
|---|---|---|---|
| [**Moniguard**](products/moniguard/) | Pay-on-delivery and e-commerce fraud scoring (`0–1000` plus reason codes). PR-AUC **0.959** (95% CI 0.942–0.972) batch, **0.837** through the API, on a 60k **synthetic** time-split benchmark. | Python, XGBoost, scikit-learn, FastAPI, Airflow, MLflow, Docker | [Case study](products/moniguard/) · [Repo](https://github.com/ikebude/MLOps-Fraud-Detection) |
| [**BI Operations Agent**](products/bi-operations-agent/) | Plain-English questions to guarded `SELECT` queries over a YAML semantic layer, daily KPI monitoring and weekly summaries. On **synthetic** retail data: **96.0%** in-sample, **56.0%** held-out, **12/12** adversarial prompts blocked, **36.6 ms** p95. | Python, FastAPI, SQLite, sqlglot, Streamlit | [Case study](products/bi-operations-agent/) · [Repo](https://github.com/ikebude/AIMLOps-BI-Operations-Agent) |
| [**AIOps Expense Tracker**](products/expense-tracker/) | NGN personal and SME finance app, extended from a course starter: TF-IDF + logistic regression categoriser (**0.9204** macro-F1), receipt-text parsing (no OCR), MAD anomaly detection (F1 **0.973**), ETS forecast (**8.1%** holdout WAPE), all on **synthetic** data. | Python, scikit-learn, FastAPI, React, Vite | [Case study](products/expense-tracker/) · [Repo](https://github.com/ikebude/AIOps_Expense_Tracker) |
| [**Lolo's Ledger**](products/lolos-ledger/) | Multi-asset trading journal and position-sizing risk engine with an educational AI analyst that never gives trading signals. NestJS + React + BullMQ monorepo built on the engine (and 349 core tests) of my desktop journal FXLedger v1.1.0. | TypeScript, React, NestJS, PostgreSQL, Redis, Python, Playwright | [Case study](products/lolos-ledger/) · source private |
| [**LoanLens**](products/loanlens/) and [**Customer Intelligence**](products/customer-intelligence/) | Product pages for the two strongest ML projects below. | Python, scikit-learn, Streamlit | see section 3 |

---

## 2. Work at 3Consulting Limited (`industry-work/`)

Engineering case studies only: the problem, the architecture and my part in it. No company source code is published here, and none of these products is presented as live; each public site is marked *deployment pending verification*.

| Platform | Domain | My part | Case study |
|---|---|---|---|
| [**SafeData**](industry-work/safedata/) | Data retention and consent governance (NDPA, GDPR) | Retention and consent-lifecycle logic, PostgreSQL test suite, CI security scanning | [Read](industry-work/safedata/) |
| [**FraudGuard**](industry-work/fraudguard/) | Transaction fraud prevention | Feature engineering, ensemble scoring pipeline, Airflow/MLflow retraining, analyst dashboard | [Read](industry-work/fraudguard/) |
| [**Africa Stablecoin Intelligence**](industry-work/africa-stablecoin-intelligence/) | Market and regulatory intelligence | Market and regulatory data schema, Light/Dark/System UI, launch and indexing preparation | [Read](industry-work/africa-stablecoin-intelligence/) |

FraudGuard is 3Consulting's product and Moniguard is my personal project. They are separate codebases, and no metric is reported for both.

---

## 3. Machine learning projects (`machine-learning/`)

Each project has pinned requirements, tests that regenerate `reports/` and `img/`, and a Limitations section.

| Project | Question | Headline result | Folder |
|---|---|---|---|
| **LoanLens: Prosper credit risk** | Which loans will default, judged on later loans? | Out-of-time ROC-AUC 0.705, KS 0.303; policy simulator at a 25% PD cutoff | [`prosper-loan-risk/`](machine-learning/prosper-loan-risk/) |
| **Customer Intelligence: telco churn, RFM, CLV** | Who should the retention team call first? | Calibrated GBDT PR-AUC 0.841 (logistic baseline 0.831), 80.5% precision at a 20% call budget | [`customer-retention/`](machine-learning/customer-retention/) |
| **NYC taxi fare and duration** | How well can a fare be quoted before the trip? | Fare MAE $1.47 (R² 0.95) on an out-of-time quarter, 29.6% lower than a linear baseline | [`tlc-cab-fare-intelligence/`](machine-learning/tlc-cab-fare-intelligence/) |
| **Waze user churn** | Which users are about to churn? | PR-AUC 0.379, ROC-AUC 0.745; the logistic baseline was as good as the tree models | [`waze-churn-prediction/`](machine-learning/waze-churn-prediction/) |
| **S&P 500 clustering and outliers** | How do constituents group on fundamentals? | 3 K-Means regimes (silhouette 0.37); market-cap tier macro-F1 0.869 vs 0.656 baseline | [`sp500-analysis/`](machine-learning/sp500-analysis/) |
| **Car pricing** | What drives MSRP once dealer invoice is excluded? | Gradient boosting R² 0.866, MAPE 12.3% on 86 test vehicles | [`cars-model-analysis/`](machine-learning/cars-model-analysis/) |

---

## 4. Analytics, BI and SQL (`analytics-and-bi/`)

| Project | Focus | Folder |
|---|---|---|
| **CRM sales pipeline** | Win rate, cycle time and SKU mix across 8,800 B2B opportunities | [`crm-sales-analysis/`](analytics-and-bi/crm-sales-analysis/) |
| **Power BI dashboards** | Churn, contact-centre SLA and HR diversity dashboards with DAX measures | [`power-bi-dashboards/`](analytics-and-bi/power-bi-dashboards/) |
| **SQL: Danny's Diner** | PostgreSQL CTEs, window functions and conditional logic answering 10 loyalty questions | [`sql-querying/`](analytics-and-bi/sql-querying/) |
| **KPMG and PwC simulations** | Data-quality audit, customer valuation and retention analysis in Python, R, Tableau and Power BI | [`bi-analytics/`](analytics-and-bi/bi-analytics/) |
| **Exploratory analyses** | Housing, weather, Netflix, cars and COVID-19 datasets in Python and R | [`global-data-analytics/`](analytics-and-bi/global-data-analytics/) |

---

## 5. How this repository is kept honest

1. **Numbers come from code.** Every ML metric here is written by the project's own pipeline to `reports/*.json`; product numbers come from the product repos' reports. Synthetic data is always labelled.
2. **Metrics that fit the problem.** Imbalanced problems report PR-AUC, recall at a fixed contact or alert budget, calibration and 95% bootstrap intervals, next to a simple baseline.
3. **Confidentiality.** Company work is described, never published.
4. **CI.** [`ci.yml`](.github/workflows/ci.yml) checks links, runs every project's tests, and fails if regenerated results differ from the committed ones.

A slide deck and LinkedIn carousels are in [`showcase/`](showcase/); see the notes there before sharing them.
