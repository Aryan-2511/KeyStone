# Exec-plan: M1-02 — P2 (Prompt Injection × Rapid-movement) through the framework

- **Slug:** `p2-rapid-movement`
- **Feature IDs:** KS-0602 (M1-02) — done; unblocks KS-0603 (M1-03 / P3)
- **Status:** done
- **Started:** 2026-06-23
- **Owner (session):** agent (Claude)

## Goal & acceptance

Add the seam matrix's second pair through the **unchanged** M1-01 framework: a
memo-borne injection driving fast onward movement, independently caught by
`core.fatf` rapid-movement (memo-blind). Axis-A (same attack class as P1, a new
typology). Acceptance = KS-0602 `done_criteria`: P2 binds CLEAN on a shared tx id;
the anti-collapse distinctness guard holds (P2 fires RAPID_MOVEMENT, not STRUCTURING);
independence + drift inherited; P1 + all prior tests stay green, untouched.

## Context / constraints

- NO framework changes (if P2 needed them, STOP — M1-01 was incomplete). None were needed.
- NO RunResult/schema/UI changes. NO touching P1. Core+assurance only.
- Independence is non-negotiable: the rapid-movement signal comes from
  amounts/timing/recipients alone (the framework's `FinancialProjection`, memo-blind).
- M1-00 §4 (P2), §6 (collapse risk).

## Plan

- [x] Recon: confirm `_detect_rapid_movement` is distinct from `_detect_structuring`.
- [x] Core substrate: `rapid_movement_cluster` + `rapid_sample_stream`
      (`RAPID_SAMPLE_STREAM_CONFIG`) — additive; P1's `sample_stream` byte-identical.
- [x] Attack side: `MEMO_FORWARDING_SIGNATURE` + `CANONICAL_FORWARDING_EXPLOIT`
      (+ `ExploitOutcome.UNAUTHORIZED_ONWARD_TRANSFER`) in `signature.py`.
- [x] `keystone.assurance.seam_p2`: `resolve_forwarding_signature`, `p2_fraud_stream`,
      `P2_PAIR`; register in `REGISTERED_PAIRS`; export from the package `__init__`.
- [x] `tests/test_seam_p2.py`: strong binding, memo-blindness, distinctness guard, drift.
- [x] Verify: `make verify` green.
- [x] Update `feature_list.json` (KS-0602 done, KS-0603 planned) + human views + docs.

## Progress log

- 2026-06-23 recon found P1's structuring cluster ALSO trips rapid-movement (see Decisions).
- 2026-06-23 built P2 (rapid-only cluster, sub-band) through the unchanged framework.
- 2026-06-23 `make verify` green: 329 passed, 2 skipped, 95.23% coverage; mypy strict /
  Ruff / import-linter clean, no new ignores. P1 byte-identical (its tests + demo green).

## Decisions

- **The framework was NOT changed** — P2 is purely a new instance. Confirms M1-01's
  abstraction generalises (the headline M1-02 result).
- **Distinctness guard is asymmetric, by necessity (a finding).** P1's dense structuring
  cluster ALSO trips RAPID_MOVEMENT incidentally, and P1's stream is off-limits. So the
  load-bearing anti-collapse assertion is **P2's exclusivity** (fires RAPID_MOVEMENT, NOT
  STRUCTURING) — STRUCTURING is the discriminator. We do NOT assert "P1 never fires
  rapid-movement" (false). Documented in `test_p1_and_p2_are_detector_distinct` and MEMORY.

## Open questions / blockers

- Should P1's structuring stream eventually be tightened so it is structuring-EXCLUSIVE
  (so the matrix's per-pair typologies are mutually exclusive)? Out of scope here (don't
  touch P1); flag for the M1-06 result write-up. Not a blocker — P1 binds STRUCTURING
  unambiguously regardless.

## Next steps (resume here)

M1-03 / KS-0603 — P3 (prompt-injection × large-transfer). Author a `SeamPair` whose
`plant` produces a SINGLE `>= ctr_threshold` (10_000) transfer that fires
`LARGE_TRANSFER` and is distinct from P1's sub-threshold band and P2's fast fan-out.
Mirror `seam_p2`; register in `REGISTERED_PAIRS` (independence + drift tests cover it
for free). Note: P1/P2 streams do NOT fire LARGE_TRANSFER (all sub-CTR), so P3's
discriminator (a single large transfer) is clean.

## Handoff (fill in on completion)

- **Changed:** `core.transactions.generator` (+`rapid_movement_cluster`,
  `rapid_sample_stream`, `StreamConfig.rapid_clusters`); `assurance.signature`
  (+P2 signature/exploit/outcome); new `assurance.seam_p2`; `assurance.pairs`
  registers P2; package `__init__` exports; new `tests/test_seam_p2.py`; docs
  (MEMORY, TASKS, feature_list KS-0602 done + KS-0603).
- **Verified:** `make verify` green — 329 passed / 2 skipped / 95.23% cov; lint +
  mypy strict + import-linter clean, no new ignores. **Framework unchanged. P1 untouched.**
- **Deferred:** P3–P5 (M1-03..05), the matrix result (M1-06); whether to make P1
  structuring-exclusive (above).
- **Recommended next task:** M1-03 / KS-0603 (P3 large-transfer).
