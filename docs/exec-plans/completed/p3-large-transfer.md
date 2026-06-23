# Exec-plan: M1-03 — P3 (Prompt Injection × Large-transfer) through the framework

- **Slug:** `p3-large-transfer`
- **Feature IDs:** KS-0603 (M1-03) — done; unblocks KS-0604 (M1-04 / P4 the BOUNDARY)
- **Status:** done
- **Started:** 2026-06-23
- **Owner (session):** agent (Claude)

## Goal & acceptance

Add the seam matrix's third pair through the **unchanged** M1-01 framework: a
memo-borne injection driving a SINGLE threshold-breaching transfer, independently
caught by `core.fatf` large-transfer (memo-blind). Completes Axis A (one attack class
→ three distinct typologies). Acceptance = KS-0603 `done_criteria`: P3 binds CLEAN on a
shared tx id; the distinctness guard holds in full (P3 fires LARGE_TRANSFER and NEITHER
other typology — the cleanly-exclusive pair); independence + drift inherited; P1, P2,
all prior tests stay green, untouched.

## Context / constraints

- NO framework changes (if needed → STOP). None were needed.
- NO RunResult/schema/UI changes. NO touching P1 or P2. NO memo into the detector.
- P1/P2 streams are all sub-CTR (<$10k), so a single ≥$10k transfer is P3's clean,
  unambiguous discriminator. M1-00 §4 (P3).

## Plan

- [x] Confirm P1/P2 streams do not fire LARGE_TRANSFER (clean discriminator).
- [x] Core substrate: `large_transfer` + `large_sample_stream`
      (`LARGE_SAMPLE_STREAM_CONFIG`, `StreamConfig.large_transfers`) — additive;
      P1/P2 `sample_stream`/`rapid_sample_stream` byte-identical.
- [x] Attack side: `MEMO_LARGE_TRANSFER_SIGNATURE` + `CANONICAL_LARGE_TRANSFER_EXPLOIT`
      (+ `ExploitOutcome.UNAUTHORIZED_LARGE_TRANSFER`) in `signature.py`.
- [x] `keystone.assurance.seam_p3`: `resolve_large_transfer_signature`,
      `p3_fraud_stream`, `P3_PAIR`; register in `REGISTERED_PAIRS`; export from `__init__`.
- [x] `tests/test_seam_p3.py`: strong binding, memo-blindness, full-exclusivity
      distinctness, drift.
- [x] Verify: `make verify` green.
- [x] Update `feature_list.json` (KS-0603 done, KS-0604 planned) + human views + docs.

## Progress log

- 2026-06-23 confirmed P1/P2 don't fire LARGE_TRANSFER; built P3 (single $18.4k transfer).
- 2026-06-23 P3 binds CLEAN through the unchanged framework; fires LARGE_TRANSFER only.
- 2026-06-23 `make verify` green: 339 passed, 2 skipped, 95.31% coverage; mypy strict /
  Ruff / import-linter clean, no new ignores. P1/P2 byte-identical & green.

## Decisions

- **Framework NOT changed** — P3 is a pure new instance (third confirmation M1-01
  generalises).
- **P3 is the cleanly-exclusive pair** — a single transfer cannot trip structuring's
  `>= 3` band or rapid-movement's `>= 5` velocity rule, so its distinctness guard
  asserts full exclusivity (LARGE_TRANSFER only), with NO overlap caveat (unlike P1).
  Axis A is now demonstrably small-many / fast-onward / single-large.

## Open questions / blockers

- None for P3. (The P1-also-fires-rapid-movement note from M1-02 still stands for the
  M1-06 result write-up; P3 is unaffected — it is fully exclusive.)

## Next steps (resume here)

M1-04 / KS-0604 — P4, THE BOUNDARY (Axis B; OWASP LLM06 sensitive-information
disclosure). Represent it as a `SeamPair` with `result=SeamResult.BOUNDARY`: an exfil/
data-loss attack that moves NO money, so the crime detector fires ZERO typologies and
the seam provably does NOT bind. The framework ALREADY supports this (proven by the
boundary stub in `tests/test_seam_framework.py`); P4 makes it a real, registered pair.
Do NOT force a weak positive — the clean negative is P4's value. The `plant` should
produce an event whose financial stream fires nothing (e.g. empty / benign), with the
attack riding the `EXFIL` channel.

## Handoff (fill in on completion)

- **Changed:** `core.transactions.generator` (+`large_transfer`, `large_sample_stream`,
  `StreamConfig.large_transfers`); `assurance.signature` (+P3 signature/exploit/outcome);
  new `assurance.seam_p3`; `assurance.pairs` registers P3; package `__init__` exports;
  new `tests/test_seam_p3.py`; docs (MEMORY, TASKS, feature_list KS-0603 done + KS-0604).
- **Verified:** `make verify` green — 339 passed / 2 skipped / 95.31% cov; lint +
  mypy strict + import-linter clean, no new ignores. **Framework unchanged. P1/P2 untouched.**
- **Deferred:** P4–P5 (M1-04..05), the matrix result (M1-06).
- **Recommended next task:** M1-04 / KS-0604 (P4 — the boundary).
