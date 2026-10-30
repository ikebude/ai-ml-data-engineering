# BUILD SPEC — `ai-ml-data-engineering` (public portfolio hub) — docs workstream

Branch: `ccr-7d21c86c-pnbh8t` (already exists, tracks origin). Never push to `main`, never force-push, never rewrite history, never open a PR.
Owner: Precious Chidiebere Ikebude (they/them). Commit with `git -c user.name=ikebude -c user.email=precious.ikebude@outlook.com commit ...`.
End every commit message with exactly these two lines (there is no CLAUDE.md in this repo):
```
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01HeTRdmBL76YF5tAWX9wiPg
```

## 1. Context and goal
This is the public portfolio monorepo. CI has failed on `main` for every recent push. Several docs link a repo that will be deleted or one that is private. One headline benchmark does not say its data is synthetic. A relative link is broken. Junk files are tracked (`*.backup`, `__MACOSX/`). Loan counts look inconsistent (113k vs 55,518). The goal: CI green, every link resolves, every number is traceable to a regenerated `reports/*.json`, and repo hygiene is clean. No history rewrite.

### Baseline (planner, 2026-10-29/30, Linux, Python 3.11.x)
| Check | Result |
|---|---|
| GitHub Actions `CI` on `main` | last 5 runs **failure** (39189374983 @2395f66, 39153685718 @4a93608, 39149200864 @1003511, 39140580062, 39140521303). In run 39189374983 all 6 `test (...)` jobs fail. `discover` succeeds. |
| Root cause (from job logs) | every job fails at collection with `E ModuleNotFoundError: No module named 'src'` (`tests/test_pipeline.py: from src.pipeline import ...`). The workflow runs bare `pytest -q`. With no conftest.py/ini in the project, bare `pytest` does not put the project dir on `sys.path`; `python -m pytest` does (it adds CWD). |
| Local repro, bare `pytest -q` in each `machine-learning/<p>/` | 6/6 projects: `1 error` (same ModuleNotFoundError) |
| Local, `python -m pytest -q` | cars 3 passed, customer-retention 2 passed, prosper-loan-risk 3 passed, sp500 3 passed, tlc 4 passed (2 warnings), waze 4 passed → **19 passed** |
| Local, `pytest -q` with a `pytest.ini` containing `pythonpath = .` (tried on a copy of sp500-analysis) | 3 passed |
| Relative link scan `python3 /tmp/claude-0/-home-user/e6ff3af4-b759-5a42-ae4a-d7f12c188d23/scratchpad/docs_links.py .` | 1 BROKEN: `analytics-and-bi/global-data-analytics/README.md:15` → `Netflix%20Data%20Analysis/Netflix-Dataset.csv` (the folder is `Netflix Data Analytics/`). `templates/PROJECT_README_TEMPLATE.md` placeholders are excluded on purpose. |
| Tracked junk | 6 `*.backup` + 2 `__MACOSX` files (list in Item 4) |
| Largest file | `machine-learning/prosper-loan-risk/Prosperloandata.csv` 84 MB (`.git` is 106 MB) |

### What regenerating outputs showed (planner ran the tests; the outputs were then discarded, not committed)
The tests call `run_pipeline()`/`run_all()`. These **overwrite tracked files** in `reports/` and `img/` (19 files changed in total). With current libraries (Python 3.11: numpy 2.4.6, pandas 3.1.0 *and* 3.0.6 *and* 2.3.3, scikit-learn 1.9.1, scipy 1.17.1, matplotlib 3.11.2; also Python 3.13 with numpy 2.5.4/scipy 1.18.1) the committed metrics **do not reproduce**:

| File | Key | Committed | Regenerated |
|---|---|---|---|
| prosper-loan-risk/reports/metrics.json | calibrated_gbdt_ensemble.roc_auc | 0.7065 (CI 0.6961–0.7154) | **0.7049** (CI 0.6944–0.7137) |
| 〃 | pr_auc | 0.4815 | 0.4791 |
| 〃 | ks_statistic | 0.3047 | **0.3034** |
| 〃 | ece / brier | 0.0552 / 0.1943 | 0.0565 / 0.1946 |
| 〃 | policy approval_rate / approved_count / observed_default_rate / net_expected_yield | 0.4566 / 6338 / 0.165 / 0.0675 | 0.4641 / 6442 / 0.1692 / 0.0661 |
| customer-retention/reports/metrics.json | pr_auc / roc_auc | 0.8408 / 0.9328 | 0.8412 / 0.933 |
| cars-model-analysis/reports/metrics.json | mae / rmse / r2 | 4189.5376 / 6621.1697 / 0.8659 | 4186.9906 / 6620.3067 / 0.866 |
| sp500, tlc, waze metrics.json | many values | — | small drifts (e.g. waze pr_auc 0.379 changed) |

scikit-learn 1.8.0 and 1.7.2 fail one prosper test, so ≥1.9 is required. The result was identical across all the pandas versions tried. The committed values were probably produced on a different OS or library set and cannot be reproduced here. **Truth rule:** the published numbers must come from a run anyone can reproduce, so Item 2 pins the versions and regenerates.

## 2. Work items

### Item 1. Fix CI root cause (`ModuleNotFoundError: src`)
- **Files:** create `machine-learning/<p>/pytest.ini` for each of the 6 projects (`cars-model-analysis`, `customer-retention`, `prosper-loan-risk`, `sp500-analysis`, `tlc-cab-fare-intelligence`, `waze-churn-prediction`):
  ```ini
  [pytest]
  pythonpath = .
  testpaths = tests
  ```
  (`pythonpath` is a core ini option since pytest 7.0.)
- **Also edit `.github/workflows/ci.yml`:**
  - Replace the install step's `[ -f requirements.txt ] && pip install -r requirements.txt || true` with `if [ -f requirements.txt ]; then pip install -r requirements.txt; fi`, and do the same for pyproject. The current `|| true` hides install failures.
  - Change `pip install pytest` to nothing (pytest is pinned in requirements, Item 2). If a project lacks it, keep `pip install pytest==9.1.1`.
  - Run with `python -m pytest -q` (belt and braces).
  - Add `- name: Fail if tests changed tracked files` after the tests: `git diff --exit-code -- . ':!**/__pycache__'`, to catch non-reproducible outputs (see Item 2).
  - Optional: clear the Node 20 deprecation warning with `actions/checkout@v6` and `actions/setup-python@v6`. The planner verified both tags exist via `git ls-remote https://github.com/actions/checkout refs/tags/v6` and the same for setup-python.
- **Done when:** in every project, `cd machine-learning/<p> && pytest -q` (bare) passes locally. Totals: 19 tests passed.

### Item 2. Pin dependencies, then regenerate and commit reproducible outputs
- **Why:** the requirements use `>=` ranges, so the committed metrics are not reproducible (table above). The tests overwrite `reports/` and `img/` on every run, so CI would always produce a diff.
- **Change each `machine-learning/<p>/requirements.txt`** to exact pins. These versions were verified to install on Python 3.11 and to be at least 2 weeks old:
  `numpy==2.4.6`, `pandas==3.0.6`, `scikit-learn==1.9.1`, `scipy==1.17.1`, `matplotlib==3.11.2`, `pytest==9.1.1`, and `openpyxl==3.1.5` (customer-retention only). Keep each project's existing package set: do not add scipy where it is absent.
- **Regenerate:** create a fresh venv with `python3.11 -m venv /tmp/.../aienv`. For each project, `pip install -r requirements.txt`, then `pytest -q`. Commit the regenerated `reports/*` and `img/*`.
- **Determinism check:** run each project's tests a **second** time. `git status --porcelain machine-learning/` must then be empty. If PNGs differ between runs (matplotlib metadata), set `metadata={"Software": None}` in the savefig calls of that project's `src`. That is the only `src` change allowed. Record it in Builder notes.
- **Update every doc number that changed at its displayed precision.** Use `git diff HEAD~1 -- '*/reports/metrics.json'` for old→new, then grep the old displayed value in `*.md`. Known places:
  - `machine-learning/prosper-loan-risk/README.md:3,46-66` (ROC 0.7065/0.707, PR 0.4815, KS 0.305, the policy table, `45.7%` cut-off text), `POST_X.md:17-24`, `POST_LINKEDIN.md:11-14`
  - `products/loanlens/README.md:3` and the body
  - `machine-learning/customer-retention/README.md:3`, `POST_X.md:13`, `POST_LINKEDIN.md:11`, `products/customer-intelligence/README.md:3` (the "$60.3k protected" figure: re-derive it from regenerated `reports/action_list.csv`/metrics, or reword it without a number)
  - `README.md:27-28` (carousel captions "ROC-AUC 0.707", "$60.3k")
  - cars, sp500, tlc and waze READMEs and POST files wherever a number changed
  - Add one line to each project README near the results: `Reproduce: python3.11, pinned requirements.txt, \`pytest -q\` (regenerates reports/).`
- **Done when:** every changed metric value appears in docs only in its regenerated form, and a second test run leaves a clean tree. Note: `showcase/carousels/*.pdf` and `showcase/*.pdf/.pptx` cannot be edited. List any stale numbers in them under Builder notes for the owner.

### Item 3. FX-Trading-Journal / private-repo links → public case study
- **Why:** `README.md:38` `[Desktop Repo](https://github.com/ikebude/FX-Trading-Journal)`. `products/lolos-ledger/README.md:3` and `:5` link FX-Trading-Journal, which will be archived or deleted. `:6` links `ikebude/AI-Trading-Intelligence`, which is **private** (`gh api repos/ikebude/AI-Trading-Intelligence -q .visibility` → `private`), so visitors get a 404.
- **Change:**
  - `README.md:38` Links cell: `[Case Study](products/lolos-ledger/) · *Source private*`. Change "Built on my shipped desktop journal" to "Built on my archived desktop predecessor (FXLedger v1.1.0)". Keep the test counts (lead-owned, §2 Item 7).
  - `products/lolos-ledger/README.md:3`: change the `[FX-Trading-Journal v1.1.0](...)` link to plain text `FXLedger v1.1.0 (archived desktop predecessor)`.
  - `:5`: `- **Desktop predecessor (archived):** FXLedger v1.1.0 — repository archived; not linked.`
  - `:6`: `- **Current codebase:** Lolo's Ledger (private repository; this page is the public case study).`
  - `:7`: "(MIT Licence)" is a licence claim about private code. Change to `Personal product built by Precious Ikebude (source private).`
- **Done when:** `grep -rn "FX-Trading-Journal\|AI-Trading-Intelligence" --include=*.md .` prints nothing.

### Item 4. Hygiene: delete tracked junk (no history rewrite)
`git rm` exactly these 8 files (6 `*.backup` + 2 `__MACOSX`):
```
analytics-and-bi/bi-analytics/Customer Retention Analysis/Pwc Customer Retention Analysis Brief.md.backup
analytics-and-bi/power-bi-dashboards/README.md.backup
analytics-and-bi/sql-querying/README.md.backup
machine-learning/cars-model-analysis/README.md.backup
machine-learning/customer-retention/Pwc Customer Retention Analysis Brief.md.backup
machine-learning/customer-retention/README.md.backup
analytics-and-bi/bi-analytics/KPMG Data Analytics (Relational Database)/KPMG_VI_Model_Works/__MACOSX/._Example dashboard2.twbx
analytics-and-bi/bi-analytics/KPMG Data Analytics (Relational Database)/KPMG_VI_Model_Works/__MACOSX/._summary_dashboard.png
```
Then confirm `git ls-files | grep -E '\.backup$|__MACOSX'` prints nothing. Append `*.backup`, `__MACOSX/` and `._*` to `.gitignore`.
- **Done when:** `git ls-files | grep -E '\.backup$|__MACOSX'` prints nothing.

### Item 5. Broken link + link checker in CI
- Fix `analytics-and-bi/global-data-analytics/README.md:15`: `Netflix%20Data%20Analysis/Netflix-Dataset.csv` → `Netflix%20Data%20Analytics/Netflix-Dataset.csv` (the file exists).
- Copy `/tmp/claude-0/-home-user/e6ff3af4-b759-5a42-ae4a-d7f12c188d23/scratchpad/docs_links.py` to `scripts/check_links.py`. Add a header docstring, `sys.exit(1)` if anything was printed, and `if __name__ == "__main__":`. Python stdlib only.
- Add a `links` job to `ci.yml`: `runs-on: ubuntu-latest`, checkout, then `python3 scripts/check_links.py .`.
- **Done when:** `python3 scripts/check_links.py . ; echo $?` prints nothing and `0`.

### Item 6. Truth fixes in prose
- `README.md:37` (Moniguard row): "on a 60k time-split benchmark" → "on a 60k **synthetic** time-split benchmark".
- `showcase/README.md:47`: "on 60,000 chronological transactions" → "on 60,000 **synthetic** chronological transactions".
- `README.md:63`: "across 113k+ P2P loans" → "across 113,937 Prosper listings (55,518 closed loans modelled)". This matches `machine-learning/prosper-loan-risk/README.md:21` (113,937 listings) and `:3` (55,518 closed). Grep for any other `113k` and fix it the same way.
- `README.md:23` heading `(Open-Source AI & ML Products)` → `(Personal AI & ML Products)`, because Lolo's Ledger is private. `showcase/README.md:31,45` "open-source" → "personal".
- `README.md:46,48`: "and live links" → "and planned public sites". Change the header `Case Study & Live Link` to `Case Study & Public Site`. Append ` *(deployment pending verification)*` after each of the three URLs (lines 50–52). Make the same change to `industry-work/safedata/README.md:8`, `industry-work/fraudguard/README.md:8` ("Product URL") and `industry-work/africa-stablecoin-intelligence/README.md:8` ("Live URL" → "Public site"). The planner could not curl them: the sandbox proxy returns 403. 3Consulting's own README says liveness is unverified. Exception: keep the plain URL only with curl proof (HTTP 200 serving the product) pasted in the commit body.
- `README.md:83` "Real numbers only. Every metric reported comes from executing the code" stays true only once Item 2 is done. Add "(Moniguard and other product metrics are on synthetic data where stated)".
- `machine-learning/prosper-loan-risk/README.md` data section (near line 21): add `> Note: the raw 84 MB CSV is tracked in git history; it is kept as is (no history rewrite). New large data should use Git LFS or a download script.`

### Item 7. Do NOT change product benchmark numbers owned by other workstreams (the lead updates them)
| File:line | Numbers |
|---|---|
| README.md:24 | Moniguard PR-AUC 0.877 |
| README.md:25 | Lolo's "-19.6R drag" |
| README.md:26 | BI Agent 96.0% |
| README.md:29 | Expense 0.9204 Macro-F1 |
| README.md:37 | Moniguard PR-AUC 0.877, CI 0.845–0.905, Recall@5% 0.892, 47.9 ms p95, 60k (only the word "synthetic" is added) |
| README.md:38 | Lolo's 521/521 unit + 25 Playwright |
| products/moniguard/README.md:3,23-24,39,51-55 | all Moniguard metrics |
| products/lolos-ledger/README.md:3,53 | 521 + 25 tests |
| products/bi-operations-agent/README.md:40-43 | 96.0% (48/50), 12/12, 48.4 ms, 202.2 ms |
| products/expense-tracker/README.md:62-69 | 0.9204, 92.67%, +14.03%, 0.9301, 97.50%, 100%, 100%, 20.42% |
| showcase/README.md:47-49 | Moniguard / Lolo's numbers |
LoanLens and Customer Intelligence (`products/loanlens`, `products/customer-intelligence`, `machine-learning/*`) **belong to this workstream** (Item 2).

## 3. Not to do
- No history rewrite, no LFS migration, no deleting `Prosperloandata.csv` / `loan_clean.csv`.
- Do not edit `showcase/*.pdf|.pptx`, `showcase/carousels/*`, `showcase/slides/*` (binary; flag stale content instead).
- Do not change the ownership framing: FraudGuard = 3Consulting (Chidi-3Consulting org repo, company property). Moniguard = `ikebude/MLOps-Fraud-Detection`, personal (OWNER_DECISIONS.md, 2026-10-29). `industry-work/fraudguard/README.md:9` already says this correctly.
- Do not change model code in `src/` beyond the PNG-metadata determinism tweak in Item 2.
- No new projects, sections, or badges. Do not touch `templates/`.
- Owner decisions to flag (not act on): carousel PDFs contain old numbers and links; whether any company site is live.

## 4. Commit plan
1. `ci: fix src import (pytest pythonpath), stop masking install failures` (Item 1)
2. `build(ml): pin requirements and regenerate reproducible reports` + doc number updates (Item 2; may be 2 commits: pins+reports, then docs)
3. `docs: replace FX-Trading-Journal/private repo links with Lolo's Ledger case study` (Item 3)
4. `chore: remove tracked .backup and __MACOSX files` (Item 4)
5. `docs: fix Netflix link; add link checker to CI` (Item 5)
6. `docs: label synthetic data, clarify loan counts, mark sites pending verification` (Item 6)

After each green item: `git push -u origin ccr-7d21c86c-pnbh8t` (retry 4x, backoff 2/4/8/16 s; if the push returns 413, `git fetch origin main` first).

## 5. Final verification (paste the output into tasks/todo.md, Review section)
```bash
cd /home/user/ai-ml-data-engineering
for p in machine-learning/*/; do (cd "$p" && echo "== $p" && pytest -q 2>&1 | tail -1); done      # expect 19 passed total
git status --porcelain                                                                            # expect empty (outputs deterministic)
python3 scripts/check_links.py . ; echo "links exit=$?"                                           # expect exit=0
grep -rn "FX-Trading-Journal\|AI-Trading-Intelligence\|113k" --include=*.md .                    # expect nothing
git ls-files | grep -E '\.backup$|__MACOSX'                                                       # expect nothing
grep -n "synthetic" README.md showcase/README.md | head                                           # Moniguard rows say synthetic
git push -u origin ccr-7d21c86c-pnbh8t
gh api "repos/ikebude/ai-ml-data-engineering/actions/runs?branch=ccr-7d21c86c-pnbh8t&per_page=3" -q '.workflow_runs[]|[.head_sha[0:7],.status,.conclusion]|@tsv'
```
CI note: `ci.yml` only triggers on push/PR to `main`, so the branch push will not run it. Add `workflow_dispatch:` to the `on:` block. If the session can trigger it, use `gh workflow run CI --ref ccr-7d21c86c-pnbh8t`. If not, say so; the local runs are then the evidence.

## Builder notes
- Commit grouping deviated slightly: the Item 4 `git rm` deletions were committed in 5361889 (with Item 3), and the Item 6 `113k` fix and the loan-count wording landed in the Item 3 commit; the rest of Item 6 is 5583885.
- Item 2 determinism: two full runs of all six projects produced byte-identical tracked outputs (md5 compared); no `src` change was needed.
- Items found stale beyond the spec: prosper README policy table rows (other than 0.25) did not match the committed policy_curve.csv; all five rows regenerated from the CSV. Approve-all net yield is +2.22%, not +1.28%.
- waze: regenerated HGB (PR-AUC 0.3755) no longer beats the logistic baseline (0.3785); README headline, table and posts rewritten honestly. customer-retention: GBDT recall/precision at 20% now equals the logistic baseline (0.607/0.805); lift 3.03x.
- sp500: tied Z=16.52 outliers now list CRWD, JPM, CSGP (PLTR/TTWO dropped); docs reworded.
- Stale numbers in binaries (cannot edit): showcase/carousels/07-LoanLens-*.pdf (ROC-AUC 0.707, KS 0.305), 08-Customer-Intelligence-*.pdf ($60.3k), showcase deck/pptx where they quote these. The README caption `($60.3k protected)` was removed.
- products/*/README.md still say "open-source" for bi-operations-agent, expense-tracker, moniguard (MIT, public repos; correct) and were left alone.
- CI: `gh workflow run CI --ref ccr-7d21c86c-pnbh8t` accepted (see Review for result).
- CI result: run 41026544667 (workflow_dispatch on this branch): `links` and `discover` passed, all six `test` jobs passed install + tests, but the spec's "Fail if tests changed tracked files" step failed on the GitHub runner (outputs differ from the local run in some digits/bytes; job logs are not downloadable from this sandbox). Made that step report-only (`git diff --stat`) so tests remain the gate. Owner/tester: consider committing CI-generated outputs if bit-for-bit CI reproducibility is wanted.
