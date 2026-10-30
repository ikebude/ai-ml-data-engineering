# TEST PLAN — `ai-ml-data-engineering` (docs workstream)

The tester verifies everything independently. Use a **fresh** Python 3.11 venv that is outside the repo (e.g. `python3.11 -m venv /tmp/claude-0/-home-user/e6ff3af4-b759-5a42-ae4a-d7f12c188d23/scratchpad/aitest`). Branch `ccr-7d21c86c-pnbh8t`.

## A. Commands and expected results
| # | Command | Expected |
|---|---|---|
| A1 | `for p in machine-learning/*/; do (cd $p && pip install -q -r requirements.txt && pytest -q \| tail -1); done` (bare `pytest`, not `python -m`) | cars 3, customer-retention 2, prosper 3, sp500 3, tlc 4, waze 4 → **19 passed, 0 errors** |
| A2 | `git status --porcelain` right after A1 | **empty**. A non-empty result means the committed outputs are not reproducible from the pinned env: FAIL Item 2 |
| A3 | `grep -E '>=|~=' machine-learning/*/requirements.txt` | nothing (all `==` pins) |
| A4 | `python3 scripts/check_links.py . ; echo $?` | no output, `0` |
| A5 | `python3 /tmp/claude-0/-home-user/e6ff3af4-b759-5a42-ae4a-d7f12c188d23/scratchpad/docs_links.py .` (independent checker) | no output |
| A6 | `grep -rn "FX-Trading-Journal\|AI-Trading-Intelligence" --include=*.md .` | nothing |
| A7 | `git ls-files \| grep -E '\.backup$\|__MACOSX'` | nothing. `.gitignore` contains `*.backup` and `__MACOSX/` |
| A8 | `grep -rn "113k" --include=*.md .` | nothing. README says 113,937 listings / 55,518 closed loans |
| A9 | `grep -n "synthetic" README.md showcase/README.md` | Moniguard row (README ~37) and showcase ~47 both say synthetic |
| A10 | `grep -n -i "open-source" README.md showcase/README.md` | nothing |
| A11 | `grep -n "pending verification" README.md industry-work/*/README.md` | 3 in README + 1 per industry README (unless a commit body has curl proof) |
| A12 | `python3 -c "import yaml,sys;yaml.safe_load(open('.github/workflows/ci.yml'))"` (or `pip install pyyaml` first) | parses. Install step has no `\|\| true`. Has the `links` job and the `git diff --exit-code` step |
| A13 | CI on GitHub: `gh api "repos/ikebude/ai-ml-data-engineering/actions/runs?branch=ccr-7d21c86c-pnbh8t"` | if a run exists: success. If none could be triggered, note it. A1/A2 are then the evidence |
| A14 | Author and trailers: `git log --format='%an <%ae>' origin/main..HEAD \| sort -u` | only `ikebude <precious.ikebude@outlook.com>`. Each body ends with the Co-Authored-By + Claude-Session lines |

## B. Adversarial checks
1. **Number drift audit (most important):** for each `machine-learning/*/reports/metrics.json`, take every metric that appears in docs (ROC-AUC, PR-AUC, KS, R², MAE, approval rate, protected revenue). Grep `*.md` for that metric's value at the displayed precision. Every doc value must equal the regenerated JSON (rounded as displayed). Specifically check LoanLens ROC-AUC (planner saw 0.7049 → "0.705", not 0.707), KS (0.3034 → "0.303"), the PD≤25% policy approval % (was 45.7%), and Customer Intelligence "$60.3k".
2. **Reproducibility attack:** delete `reports/` and `img/` in one project (`git stash`-free: copy the project to a temp dir first) and run `pytest -q`. Then diff the regenerated metrics.json against the committed one. It must be identical.
3. **CI masking:** temporarily add a bogus package to one project's requirements in a temp copy and confirm the install step would now fail. Read the yml: there must be no `|| true` on installs.
4. **Link attack:** grep for links with `%20` and parentheses in README tables. Confirm that GitHub renders them (`gh api -X POST /markdown -f mode=gfm -f text="$(cat analytics-and-bi/global-data-analytics/README.md)"` and check the `href`s).
5. **Public 404 test:** every absolute `https://github.com/ikebude/<repo>` URL in `*.md` points at a public repo (`gh api repos/ikebude/<repo> -q .visibility`).
6. **Scope fence:** `git diff --stat origin/main..HEAD` must not touch `showcase/*.pdf|pptx`, `showcase/carousels`, `templates/`, or any `src/*.py` except savefig-metadata lines. Any change to model logic is a FAIL.
7. **Ownership:** FraudGuard pages still say 3Consulting proprietary, and no page links ikebude/MLOps-Fraud-Detection as FraudGuard's source (OWNER_DECISIONS #1).
8. **Screenshots:** render the README and products/lolos-ledger/README.md at 390 px and 1280 px, light and dark, from the GitHub branch view or the gfm HTML. Tables must not break and no raw HTML may show.

## C. README claim → evidence
| Claim (file) | Evidence the tester checks |
|---|---|
| LoanLens ROC-AUC / KS / PR-AUC (README, products/loanlens, prosper README/POSTs, ikebude profile is lead-owned) | `machine-learning/prosper-loan-risk/reports/metrics.json` → `calibrated_gbdt_ensemble` |
| 55,518 closed loans / 13,880 OOT / 113,937 listings | metrics.json `total_closed_loans`, `test_loans`; `wc -l`/pandas row count of Prosperloandata.csv |
| Churn PR-AUC/ROC-AUC, 7,043 customers, revenue protected | `machine-learning/customer-retention/reports/metrics.json`, `action_list.csv` |
| Cars / S&P / TLC / Waze numbers | each `reports/metrics.json` |
| "CI discovers and runs tests on every push" (README:86) | ci.yml + A1/A13 |
| Moniguard metrics on synthetic data | wording only. Numbers are lead-owned (`/home/user/mlops-fraud-detection/reports/*.json`) |
| Lolo's 521 + 25 tests, BI 96.0%, Expense 0.9204 | lead-owned. Report mismatches as notes only |
| Company sites "pending verification" | no curl proof possible from sandbox (proxy 403) |

## Tester findings
(append: file:line, severity, description)
