# Exec-plan: M1-05 — P5, the OPEN pair (tool-misuse × unauthorized-recipient)

- **Slug:** `p5-recipient`
- **Feature IDs:** KS-0605 (M1-05) — done; unblocks KS-0606 (M1-06 the matrix result)
- **Status:** done
- **Started:** 2026-06-23
- **Owner (session):** agent (Claude)

## Goal & acceptance

Add the matrix's Axis-B pair (OWASP LLM08 tool-misuse, beyond injection) caught by a
NEW, minimal, INDEPENDENT recipient-screening typology — the only new detector in M1.
P5 is OPEN: report as-found. Acceptance = KS-0605 `done_criteria`: P5 binds as-found
(CLEAN) on a shared payment id; independence proven (the standing list fires on the
destination even with no attack present); the new typology is well-bounded and distinct;
drift-protected; P1-P4 stay green.

## PATH DECISION — PATH A (a minimal independent recipient typology)

Chosen **PATH A** (preserves Axis B). A standing flagged-destination list
(`FLAGGED_DESTINATIONS` in `core.fatf`) + a membership check is cleanly buildable,
genuinely independent (the list is attack-unaware core data; the detector reads the
destination only), and minimal (one frozenset + one check — no fuzzy matching, no feed,
no entity resolution). The three Path-A gates all held, so no fallback to Path B was
needed.

## Context / constraints

- NO framework changes (none needed). NO touching P1-P4. NO schema/UI changes.
- INDEPENDENCE non-negotiable: the screen flags the destination on STANDING-list terms,
  never because the attack named it; `FinancialProjection` already carries the
  destination (no extension needed).
- core stays attack-unaware: the standing list is core data; the EDGE references it to
  direct the tool-misuse payment (no core→edge import; no fatf→transactions cycle).

## Plan

- [x] PATH decision: confirm a minimal independent recipient screen is buildable → Path A.
- [x] core.fatf: `Typology.UNAUTHORIZED_RECIPIENT`, `FLAGGED_DESTINATIONS` standing list,
      `_detect_unauthorized_recipient` (destination-only, memo-blind), wired into `detect`.
- [x] Attack side: `TOOL_MISUSE_SIGNATURE` (channel TOOL_CALL, outcome
      UNAUTHORIZED_RECIPIENT_PAYMENT) + `CANONICAL_TOOL_MISUSE_MEMO` ([agent-tool-call]
      trace) + new enum members (InjectionField.TOOL_CALL, InjectionMechanism.EXCESSIVE_AGENCY).
- [x] `keystone.assurance.seam_p5`: `resolve_tool_misuse_signature` (bespoke marker, NOT
      the injection detector), `p5_tool_misuse_stream`, `P5_PAIR`; register; export.
- [x] `tests/test_seam_p5.py` (+ 3 core tests in `test_fatf.py` for the new typology).
- [x] Verify: `make verify` green.
- [x] Update `feature_list.json` (KS-0605 done, KS-0606 planned) + human views + docs.

## Progress log

- 2026-06-23 chose Path A; built the standing recipient screen + the LLM08 attack side.
- 2026-06-23 P5 binds CLEAN; independence proven (screen fires with no attack present).
- 2026-06-23 `make verify` green: 363 passed, 2 skipped, ~95% coverage; mypy strict /
  Ruff / import-linter clean, no new ignores. Framework unchanged; P1-P4 untouched.

## Decisions

- **PATH A**, not the §6 fallback — the recipient screen is cleanly independent + minimal.
- **The tool-call channel is synthetically represented** (the as-found caveat): our
  substrate has no separate tool-call surface, so the agent's tool-misuse is recorded as
  a `[agent-tool-call]` trace in the memo and recognised by a bespoke marker (not the
  reused injection detector — P5 is not an injection). So P5's attack-side is more
  synthetic than P1-P3's; the CRIME side is fully real and independent. Reported honestly,
  not hidden — P5 was OPEN and the result is CLEAN-with-caveat.
- **Framework NOT changed** — fifth confirmation the M1-01 abstraction generalises
  (across CLEAN, BOUNDARY, and a new typology + new attack class).

## Open questions / blockers

- None blocking. For M1-06: characterise P5 honestly (the synthetic tool-call channel)
  alongside the fully-independent recipient typology. The matrix is complete.

## Next steps (resume here)

M1-06 / KS-0606 — the characterized-mapping RESULT: surface the completed matrix
(REGISTERED_PAIRS + per-pair bindings) as a table/figure with the result distribution (4
CLEAN + 1 BOUNDARY) and the P4 boundary analysis. The RunResult/UI surface for the matrix
lands here (deferred from M1-01..05). Derive from REGISTERED_PAIRS (one source of truth).

## Handoff (fill in on completion)

- **Changed:** `core.fatf` (`UNAUTHORIZED_RECIPIENT` typology + `FLAGGED_DESTINATIONS` +
  detector); `assurance.signature` (P5 signature/trace + 3 enum members); new
  `assurance.seam_p5`; `assurance.pairs` registers P5; package `__init__` exports; new
  `tests/test_seam_p5.py` + 3 `test_fatf.py` tests; docs (MEMORY, TASKS, feature_list
  KS-0605 done + KS-0606).
- **Verified:** `make verify` green — 363 passed / 2 skipped; lint + mypy strict +
  import-linter clean, no new ignores. **Framework unchanged. P1-P4 untouched.**
- **Deferred:** the matrix result (M1-06).
- **Recommended next task:** M1-06 / KS-0606 (the characterized-mapping result + figure).
