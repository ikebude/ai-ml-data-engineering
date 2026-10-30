# Lolo's Ledger — Multi-Asset Trading Journal, Risk Engine & AI Performance Coach

> Combines my local-first desktop trading journal (FXLedger v1.1.0, archived desktop predecessor — **521/521 unit tests + 25 Playwright e2e tests passing**) with a full-stack NestJS + React + BullMQ monorepo featuring position-sizing risk guards, automated OHLC trade snapshots, and an educational AI journaling coach.

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
        MT["MT4 / MT5 Live Bridge"]
        Bin["Binance Connector"]
        CSV["Multi-Broker Importers<br/>(cTrader, IBKR, Bamboo, etc.)"]
    end

    subgraph Core["@ll/core + NestJS API + BullMQ Worker"]
        Risk["Risk & Position Engine<br/>(Lots/Units · Daily Loss Guard · Kelly)"]
        Metrics["Performance Analytics<br/>(R-Multiples · Expectancy 95% CI · Sharpe/Sortino · MAE/MFE)"]
        Psych["Discipline & Tilt Detectors<br/>(Revenge · Overtrading · Cool-down)"]
        Snap["Headless Chart Snapshot Worker<br/>(lightweight-charts PNG capture)"]
        Coach["AI Journaling Coach<br/>(Educational review of user's own stats)"]
    end

    subgraph Storage["Persistence"]
        DB[("PostgreSQL / Local SQLite<br/>+ Tamper-Evident Audit Hash Chain")]
    end

    MT & Bin & CSV --> Core
    Core --> DB
```

---

## 3. Verification & Engineering Highlights

- **521 Passing Unit Tests & 25 Playwright E2E Tests (Desktop v1.1.0):** Covers R-multiple expectancy with 95% confidence intervals, Sharpe/Sortino/Calmar ratios, MAE/MFE excursion tracking, prop-firm daily-loss circuit breakers, fuzzy-header CSV importers, and tamper-evident SHA-256 audit-log sealing.
- **Full-Stack Monorepo (`pnpm` + `Turborepo`):** Shared TypeScript `@ll/core` math/risk package, NestJS REST + webhook API (`services/api`), BullMQ background worker, PostgreSQL + Redis (`docker-compose`), and React + TanStack Router web UI (`apps/web`).
- **Offline-First & Model-Gated AI:** Local Whisper voice-memo transcription and local screenshot OCR degrade gracefully when offline; the LLM coach strictly reviews user journal data with `"Educational, not financial advice"` guardrails.
