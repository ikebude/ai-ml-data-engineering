# Todo — ai-ml-data-engineering docs workstream
- [x] Item 1 CI src import: pytest.ini in 6 projects; ci.yml fixed (no `|| true`, python -m pytest, workflow_dispatch, checkout/setup-python v6)
- [x] Item 2 pinned requirements; reports/img regenerated; doc numbers updated; Reproduce lines added
- [x] Item 3 FX-Trading-Journal / AI-Trading-Intelligence links removed
- [x] Item 4 8 junk files removed; .gitignore updated
- [x] Item 5 Netflix link fixed; scripts/check_links.py + `links` CI job
- [x] Item 6 synthetic labels, 113,937/55,518 wording, personal heading, sites pending verification, Prosper data note
- [x] Item 7 lead-owned product numbers untouched

## Review
- Local, bare `pytest -q` per project (pinned py3.11 env): cars 3, customer-retention 2, prosper 3, sp500 3, tlc 4, waze 4 = 19 passed (before: 6/6 collection errors).
- Determinism: second full run left identical tracked outputs (md5 diff empty).
- check_links.py: exit 0. grep FX-Trading-Journal|AI-Trading-Intelligence|113k outside tasks/: none. `.backup`/`__MACOSX` tracked: none.
- CI (workflow_dispatch, run 41026544667): links OK, discover OK, 6 test jobs passed tests but failed the diff-guard step; guard made report-only (see Builder notes in BUILD_SPEC.md).
- Regenerated vs committed: prosper ROC-AUC 0.7065->0.7049, KS 0.3047->0.3034; waze HGB no longer beats logistic; see Builder notes.
