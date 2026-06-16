<!--
Exec-plan. Keep it current AS YOU WORK — handoff for any future session.
On completion run the verify gate and move to docs/exec-plans/completed/.
-->

# Exec-plan: Citation-validation accuracy budget (build-failing gate)

- **Slug:** `citation-validation-gate`
- **Feature IDs:** KS-0205 (Phase 2 / Layer 3 — Obligation Mapper). Builds on
  KS-0201 (the curated graph + locked schema, ADR-0012).
- **Status:** done (archived 2026-06-17)
- **Started:** 2026-06-17
- **Owner (session):** agent

## Goal & acceptance

A standalone validator makes a **missing or malformed source citation a hard
build failure**, enforcing the per-instrument "accuracy budget" beyond the
loader's structural checks.

- **`done_criteria` (KS-0205):** "a validation test fails the build if any
  obligation node has a missing or malformed source citation."
- **QUALITY.md:** #1 tests pass · #3 scope (done_criteria + tests) · #4 mypy
  strict · #5 ruff/`S` · #6 architecture (deterministic core; no edge import) ·
  #7 docs fresh · #8 synthetic/accurate citations.

## Context / constraints

- ADR-0012 explicitly designs KS-0205 as "validate the data file against this
  schema and the per-instrument provision patterns" — mirror
  `scripts/validate_feature_list.py` (a `validate() -> list[str]` + `main() ->
  int`, run standalone, in `make verify`, and via a pytest import).
- `scripts/` is already on `pythonpath` (pyproject `[tool.pytest.ini_options]`),
  so tests can `from validate_obligations import validate`.
- The loader (`load_obligations`) already fails loud on structural defects;
  KS-0205's value-add is the **per-instrument provision-pattern** check plus
  citation sanity (no future `retrieved`, https `url`). `retrieved` is OPTIONAL
  per ADR-0012 — missing is allowed (Indian nodes carry null on purpose); only a
  *malformed* (future) date fails.
- Deterministic core boundary: the script imports only
  `keystone.core.obligations`; no LLM/edge.

## Plan

- [x] `scripts/validate_obligations.py`: `validate(path=DATA_PATH) -> list[str]`
      — load via `load_obligations` (load error => one error entry), then per
      node check provision against a per-instrument regex, reject future
      `retrieved`, require https `url` when present. `main() -> int` prints +
      exits non-zero on any error (mirror `validate_feature_list.py`).
- [x] Wire into `make verify` (standalone run next to the feature-list validator).
- [x] Tests in `tests/test_obligations.py`: shipped data passes the budget;
      malformed provision / future retrieved / non-https url / load error each
      produce errors (build would fail); optional missing `retrieved` is allowed.
- [x] `feature_list.json` KS-0205 → done + test refs.
- [x] Verify: `make verify` green; update TASKS.md + this plan's Handoff.

## Progress log

- 2026-06-17 created plan. KS-0201 (graph) + ADR-0013 (dep hygiene) already
  committed on branch `ks-0201-obligation-graph`. Starting the gate now.
- 2026-06-17 (follow-up) CI/local divergence: the future-`retrieved` check used
  local `date.today()`, flagging the correct 2026-06-17 dates as future on CI's
  UTC clock. Fixed: compare against `datetime.now(UTC).date()`, today-inclusive,
  and DEMOTE future-dated `retrieved` to a non-fatal WARNING (it is advisory per
  ADR-0012). `check()` now returns `(errors, warnings)`; `validate()` returns
  errors only. Added deterministic injected-`today` tests. See [[MEMORY.md]].

## Decisions

- **Per-instrument provision patterns** (in `scripts/validate_obligations.py`):
  EU AI Act / DORA = `^Art\. \d+$`; DPDP Act = `^s\. \d+(\(\w+\))?$`; DPDP Rules
  = `^Rule \d+$`; RBI = `^Sutra — \S.*$` (named sutra, no number — sources order
  them differently); PMLA = `^(s\. \d+|Rule \d+), \S.*$`. No ADR: this is an
  implementation detail of the gate ADR-0012 already mandated, not a new
  structural choice.
- **`retrieved` absence is allowed; a future date is a WARNING, not an error** —
  ADR-0012 marks `retrieved` optional/advisory; the Indian nodes carry null on
  purpose. The comparison is UTC-explicit and today-inclusive (`retrieved ==
  today` passes); only strictly-after-today warns.
- The gate **subsumes the loader's structural failures** (load error => one error
  entry) so `make verify` fails on either a structural or accuracy-budget defect.

## Open questions / blockers

- None. Resolved.

## Next steps (resume here)

Task complete. Recommended next: KS-0202 (control library + the 5b fail-loud
referential-integrity validator over `control_ids`), then KS-0203 (modality
contrast) and KS-0204 (LLM-edge summary phrasing).

## Handoff

- **What changed:** added `scripts/validate_obligations.py` (accuracy-budget
  validator mirroring `validate_feature_list.py`), wired it into `make verify`,
  added 6 budget tests to `tests/test_obligations.py`, flipped KS-0205 → done
  with test refs, ticked TASKS.md.
- **Verified:** `make verify` → `"verify: acceptance gate passed"`, 58 passed /
  1 skipped, mypy strict + ruff + import-linter clean, coverage 90%.
- **Deferred:** KS-0202/0203/0204 (see Next steps). The validator currently
  checks provision shape, https url, and non-future `retrieved`; a staleness
  *threshold* on `retrieved` (flag citations older than N months) was considered
  and left out — ADR-0012 lists it as optional and most Indian nodes carry no
  `retrieved` by design, so a threshold would be noise today.
- **Recommended next task:** KS-0202.
