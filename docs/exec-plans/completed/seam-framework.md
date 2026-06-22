# Exec-plan: M1-01 — the Seam Framework abstraction

- **Slug:** `seam-framework`
- **Feature IDs:** KS-0601 (M1-01) — done; unblocks KS-0602 (M1-02 / P2)
- **Status:** done
- **Started:** 2026-06-23
- **Owner (session):** agent (Claude)

## Goal & acceptance

Generalise the single `TXN-000016` seam into a framework that binds ANY
(attack-class, FATF typology) pair under ONE uniform independence guarantee and ONE
uniform build-failing drift assertion, with P1 re-expressed as the framework's first
instance. Design contract: `M1-00_SEAM_MATRIX_DESIGN.md`. Acceptance = KS-0601
`done_criteria` in `feature_list.json`:
- all existing seam tests pass with P1 bound THROUGH the framework (no assertion weakened);
- the independence guarantee is enforced framework-level (detector only sees the
  `FinancialProjection`, never the attack channel), asserted over every registered pair;
- the build-failing drift assertion fires on a forced disagreement, and a BOUNDARY
  pair's "no typology fires" negative is representable and proven by test.

## Context / constraints

- Edge-only (`keystone.assurance`); core stays attack-unaware (import-linter KEPT).
- Do NOT add P2–P5 here (M1-01 is the abstraction + P1 only). Do NOT touch RunResult/UI.
- Do NOT weaken any existing seam assertion to fit the abstraction.
- See ADR-0014 (the framework + independence-as-typed-property).

## Plan

- [x] Step-0 recon (read-only): P2 distinctness + P5 feasibility → recorded in `M1-00` §7a.
- [x] `keystone.assurance.framework` — channels, `FinancialProjection`/`project_financial`,
      `AttackSide`/`CrimeSide`/`SeamEvent`/`SeamPair`/`PairBinding`, `SeamResult`,
      `SeamDriftError`, `bind`.
- [x] Re-express P1 as `P1_PAIR` in `keystone.assurance.seam`; `prove_seam`/
      `seam_fraud_stream`/`resolve_signature` keep signatures (callers untouched).
- [x] `keystone.assurance.pairs.REGISTERED_PAIRS`; export from the package `__init__`.
- [x] `tests/test_seam_framework.py` — independence property (per registered pair),
      forced-drift (both sides) + restore, BOUNDARY stub + boundary-drift.
- [x] Verify: `make verify` green.
- [x] Update `feature_list.json` (KS-0601 done, KS-0602 planned) + human views + docs.

## Progress log

- 2026-06-23 created plan; recon done (3 distinct FATF detectors; no recipient typology).
- 2026-06-23 built framework, refactored P1 through it, added registry + tests.
- 2026-06-23 `make verify` green: 318 passed, 2 skipped, 95.12% coverage. mypy strict /
  Ruff / import-linter clean, no new ignores.

## Decisions

- **ADR-0014** — the Seam Framework; independence enforced as a *typed framework
  property* (`CrimeSide.detect` only accepts a `FinancialProjection`), asserted once
  over `REGISTERED_PAIRS`, rather than a per-pair memo-blindness test.

## Open questions / blockers

- **P5 (M1-05) needs a recipient/sanctions typology that does not exist in `core.fatf`.**
  Per `M1-00` §6 the likely path is the fallback (a clean fourth injection pair). Decide
  at M1-05 start, not before.

## Next steps (resume here)

M1-02 / KS-0602 — P2 (prompt-injection × rapid-movement). Author a `SeamPair` whose
`plant` produces a fast multi-hop onward-movement pattern that fires the existing
`RAPID_MOVEMENT` typology and is visibly distinct from P1's structuring cluster
(verify it fires rapid-movement, not just structuring). Register it in
`REGISTERED_PAIRS` — the framework's independence + drift tests then cover it for free.

## Handoff (fill in on completion)

- **Changed:** new `keystone.assurance.framework` + `.pairs`; `keystone.assurance.seam`
  re-expresses P1 as `P1_PAIR` through `bind()` (public API preserved); package
  `__init__` exports the framework; new `tests/test_seam_framework.py`; docs
  (`M1-00` §7a recon, ADR-0014, MEMORY.md, TASKS.md, ROADMAP.md, feature_list.json).
- **Verified:** `make verify` green — 318 passed / 2 skipped / 95.12% cov; lint +
  mypy strict + import-linter clean, no new ignores. All existing seam tests pass
  unchanged (faithfulness proof).
- **Deferred:** P2–P5 (M1-02..05) and the matrix result (M1-06); the P5 recipient
  typology question (above).
- **Recommended next task:** M1-02 / KS-0602 (P2 rapid-movement).
