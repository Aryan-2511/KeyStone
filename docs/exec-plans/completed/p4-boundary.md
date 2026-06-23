# Exec-plan: M1-04 — P4, the characterized BOUNDARY (exfil × none)

- **Slug:** `p4-boundary`
- **Feature IDs:** KS-0604 (M1-04) — done; unblocks KS-0605 (M1-05 / P5 the open pair)
- **Status:** done
- **Started:** 2026-06-23
- **Owner (session):** agent (Claude)

## Goal & acceptance

Add the matrix's characterized BOUNDARY (the paper's credibility anchor): an OWASP
LLM06 exfiltration attack that moves NO money, so NO typology fires and the seam
provably does NOT bind — a PROVEN, PRINCIPLED negative (not incidental, not forced).
Acceptance = KS-0604 `done_criteria`: P4 registers as `result=BOUNDARY` and binds as an
all-None proven negative; the negative is demonstrated principled (the SAME full detect
suite that fires on P1/P2/P3 fires zero on P4 — a property of the attack, not a missing
detector); the boundary is build-protected (a forced typology-fire raises
`SeamDriftError`); P1-P3 stay green.

## Context / constraints

- NO framework changes (the BOUNDARY structure exists from M1-01; if P4 needs framework
  changes → STOP). None were needed.
- NO new typology, NO forced/weak binding ("unusual access before a transfer"), NO
  touching P1-P3, NO schema/UI changes.
- The clean negative IS the result (M1-00 §4 forbids the forced positive).

## Plan

- [x] Re-read the framework BOUNDARY path (`bind`: crime.typology=None → zero of ANY
      typology must fire → all-None binding; else SeamDriftError).
- [x] Attack side: `EXFIL_INJECTION_SIGNATURE` (outcome `DATA_DISCLOSURE`) + bare string
      `CANONICAL_EXFIL_MEMO` (NOT a MaliciousMemoExample — no recipient/amount).
- [x] `keystone.assurance.seam_p4`: `resolve_exfil_signature`, `p4_exfil_event` (empty
      financial stream), `P4_PAIR` (result=BOUNDARY), `BOUNDARY_STATEMENT`; register in
      `REGISTERED_PAIRS`; export from `__init__`.
- [x] `tests/test_seam_p4.py`: proven boundary, attack-is-real, principled-negative (with
      P1/P2/P3 contrast), boundary-drift + restore, independence, boundary statement.
- [x] Verify: `make verify` green.
- [x] Update `feature_list.json` (KS-0604 done, KS-0605 planned) + human views + docs.

## Progress log

- 2026-06-23 confirmed framework BOUNDARY support; built P4 (empty stream + exfil sig).
- 2026-06-23 principled-negative proven via contrast with P1-P3 (same suite, fires zero).
- 2026-06-23 `make verify` green: 347 passed, 2 skipped, ~95% coverage; mypy strict /
  Ruff / import-linter clean, no new ignores. Framework unchanged; P1-P3 untouched.

## Decisions

- **Framework NOT changed** — the M1-01 BOUNDARY result classification was sufficient;
  P4 is the first REAL boundary pair (M1-01 only had a test stub). Confirms the boundary
  abstraction was complete.
- **Empty financial stream** is the principled representation: a data-disclosure outcome
  produces no transaction record, so there is literally no fund movement for any typology
  to act on. The principle (data loss ≠ fund movement) is anchored by the attack's
  `DATA_DISCLOSURE` outcome and proven non-incidental by the P1/P2/P3 contrast.
- **Exfil exploit is a bare string, not a `MaliciousMemoExample`** — that model carries
  money-movement fields (recipient/amount) which the boundary, by definition, lacks. The
  type difference itself reinforces the boundary.

## Open questions / blockers

- None for P4. The one-sentence boundary statement (`BOUNDARY_STATEMENT`) is ready for
  the M1-06 paper write-up.

## Next steps (resume here)

M1-05 / KS-0605 — P5, THE OPEN pair (OWASP LLM08 excessive agency / tool-misuse →
recipient screening). **Decide at the start (M1-00 §6/§7a):** `core.fatf` has NO
recipient/sanctions typology (only fund-movement typologies), so P5 needs either a new,
well-bounded recipient-screening typology OR the documented §6 FALLBACK to a clean
fourth injection×typology pair. Report P5 as-found. The framework already models the
`TOOL_CALL` channel and the `OPEN` result — no framework change expected.

## Handoff (fill in on completion)

- **Changed:** `assurance.signature` (+`EXFIL_INJECTION_SIGNATURE`, `CANONICAL_EXFIL_MEMO`,
  `ExploitOutcome.DATA_DISCLOSURE`); new `assurance.seam_p4`; `assurance.pairs` registers
  P4; package `__init__` exports; new `tests/test_seam_p4.py`; docs (MEMORY, TASKS,
  feature_list KS-0604 done + KS-0605).
- **Verified:** `make verify` green — 347 passed / 2 skipped; lint + mypy strict +
  import-linter clean, no new ignores. **Framework unchanged. P1-P3 untouched.**
- **Deferred:** P5 (M1-05) + the matrix result (M1-06).
- **Recommended next task:** M1-05 / KS-0605 (P5 — the open pair; decide typology vs §6 fallback).
