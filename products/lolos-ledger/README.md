# Lolo's Ledger — Multi-Asset Trading Journal, Risk Engine & AI Performance Coach

> Ports the engine of my local-first desktop trading journal (FXLedger v1.1.0, archived desktop predecessor), with its **349 core tests**, into a full-stack NestJS + React + BullMQ monorepo with position-sizing risk guards, per-trade chart snapshots, a Python research service and an educational AI analyst. Benchmark figures in the product repo come from a **synthetic** 240-trade journal and are not trading results, so none are quoted here.

- **Desktop predecessor (archived):** FXLedger v1.1.0 — repository archived; not linked.
- **Current codebase:** Lolo's Ledger (private repository; this page is the public case study).
- **Role & Ownership:** Personal product built by Precious Ikebude (source private).

![Lolo's Ledger — Trading Journal, Risk Engine & AI Coach](img/lolos-ledger-dark.png)

---

## 1. Problem

Retail and prop-firm traders across forex, crypto, indices, commodities, and equities lose capital primarily through position-sizing mistakes, breaking daily drawdown rules, and failing to review losing streaks objectively. Most cloud journals require expensive subscriptions, lock user data away, or push "AI trading signals" instead of helping traders measure and enforce their own process.

**Lolo's Ledger** focuses strictly on **risk discipline, quantitative trade attribution, and behavioural review**:
- **Never generates buy/sell signals or price predictions.**
- Enforces position sizing, daily loss limits, and pre-trade checklists before a trade is placed.

---

## 2. Architecture

```mermaid
flowchart LR
    subgraph Sources["Trade & Market Sources"]
        MT["MetaTrader connector<br/>+ MT4/MT5 HTML import"]
        Bin["Binance spot & futures connectors"]
        CSV["Multi-Broker Importers<br/>(cTrader, IBKR, Bamboo, etc.)"]
    end

    subgraph Core["@ll/core + NestJS API + BullMQ Worker"]
        Risk["Risk & Position Engine<br/>(Lots/Units · Daily Loss Guard · Kelly)"]
        Metrics["Performance Analytics<br/>(R-Multiples · Expectancy 95% CI · Sharpe/Sortino · MAE/MFE)"]
        Psych["Discipline & Tilt Detectors<br/>(Revenge · Overtrading · Cool-down)"]
        Snap["Chart Snapshot Worker<br/>(dependency-free PNG renderer)"]
        Coach["AI Analyst<br/>(Claude, OpenAI, Gemini or local Ollama;<br/>reviews the user's own stats)"]
    end

    subgraph Storage["Persistence"]
        DB[("PostgreSQL + Redis<br/>(desktop predecessor: SQLite)")]
    end

    MT & Bin & CSV --> Core
    Core --> DB
```

---

## 3. Verification & Engineering Highlights

- **Tests:** core (including the 349 tests ported from FXLedger v1.1.0), API, web and Python suites, plus Playwright end-to-end tests. The ported core suite covers R-multiple expectancy with 95% confidence intervals, Sharpe/Sortino/Calmar ratios, MAE/MFE excursion tracking, prop-firm daily-loss circuit breakers, and fuzzy-header broker CSV importers.
- **Full-Stack Monorepo (`pnpm` + `Turborepo`):** Shared TypeScript `@ll/core` math/risk package, NestJS REST + webhook API (`services/api`), BullMQ background worker, PostgreSQL + Redis (`docker-compose`), and React + TanStack Router web UI (`apps/web`).
- **Python Research Service:** No-look-ahead backtester with costs and ATR stops, anchored and rolling walk-forward with out-of-sample scoring, and a personal-edge model that refuses to fit below 100 closed trades.
- **Model-Gated AI:** The AI analyst can run fully offline through Ollama. Every number it writes is checked against its input, otherwise a built-in template is shown, and it never gives buy/sell signals (`"Educational, not financial advice"`). Screenshot OCR is specified but not built yet.
