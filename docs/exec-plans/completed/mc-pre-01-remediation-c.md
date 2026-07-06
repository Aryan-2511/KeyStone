# Exec-plan: MC-PRE-01 — Build remediation (c), the distinct financial-side remediation

- **Slug:** `mc-pre-01-remediation-c`
- **Feature IDs:** KS-0620 (prerequisite for Movement C / MC-00)
- **Status:** done (PR pushed, awaiting review — not self-merged)
- **Started:** 2026-07-05
- **Owner (session):** Claude (Opus 4.8)

## Goal & acceptance

The remediation probe returned MENU-FIRST: only ONE remediation existed (the AI-side
guardrail rail). Build the SECOND, genuinely-distinct remediation — (c) financial-side
detection tightening — as REAL capability, and PROVE it distinct via missed-then-caught
(baseline misses a tx that (c) catches). No defense agent (that's MC-01) — the menu option
only. Memo-blind boundary sacred. Acceptance = KS-0620 done_criteria. Stop at green + proof.

## Context / constraints

- Design basis: `remediation_probe.md` (verdict MENU-FIRST; (c) is the memo-safe 2nd option).
- (c) acts on the OPPOSITE side of the seam from (a): (a) blocks the prompt, (c) flags the money.
- SACRED: memo-blind (`engine.py:1-12`, `framework.py` `project_financial`); (c) re-runs the
  SAME memo-blind `detect()`, never the attack channel. Core stays edge-free (import-linter).
- NO defense agent, NO change to (a) / agents' logic / seam / ledger, NO schema-meaning change.

## Plan

- [x] Base clean (main @ 46a261d, all prior work merged); baseline verify green; probe doc
      brought in as design basis. Branch `mc-pre-01-remediation-c`.
- [x] Choose the form of (c): stricter `FatfThresholds` PROFILE (not flagged-destinations) —
      `detect()` already takes thresholds as a param, so zero new plumbing, pure tightening.
- [x] Build: `core.fatf.STRICT_THRESHOLDS` (CTR 10k->5k, structuring floor 5k->2.5k); new
      `keystone.assurance.remediation` (menu + `tighten_financial_detection` /
      `newly_flagged_by_tightening`); exports from both `__init__`s.
- [x] Proof test (`tests/test_remediation.py`): baseline MISSES a lone 9,000 transfer, (c)
      CATCHES it as LARGE_TRANSFER; memo-blind held; menu has 2 distinct sides; (a) unchanged.
- [x] Gates: make check / make verify green (522 passed, 2 skipped, 93.53%, pip-audit clean).
- [x] Docs: ADR-0028, OPEN_QUESTIONS (MC gate met), feature_list KS-0620, MEMORY, this plan.

## Decisions

- **Form of (c) = stricter thresholds, not flagged-destinations.** `FatfThresholds` is already a
  `detect()` parameter (`engine.py`), so a stricter profile is the intended, zero-plumbing
  extension and is pure *tightening* of existing rules. Flagged-destinations would be new list
  data and a different typology — less cleanly "the same detection, tightened."
- **STRICT_THRESHOLDS lives in core** (a `FatfThresholds` instance — core data, no edge dep);
  the remediation ACTION/menu lives in `keystone.assurance.remediation` (edge; imports core).
- **Proof tx = lone 9,000 transfer.** Just under the 10k CTR, not a cluster → baseline misses on
  every typology; strict CTR=5k → LARGE_TRANSFER. Unambiguous single-tx flip.
- **No schema bump.** Reuses `Finding`/`detect`; `STRICT_THRESHOLDS` additive; `DEFAULT_THRESHOLDS`
  byte-unchanged. Mirrors how prior tags fit without a bump.

## Proof (the whole point)

Lone transfer `TXN-…9001`, amount 9,000, normal recipient:
- baseline (CTR=10,000) → **findings: NONE** (not >=3 structuring, not >=10k, not flagged recipient).
- (c) strict (CTR=5,000) → **findings: [LARGE_TRANSFER]** on the same tx.
- `newly_flagged_by_tightening` → exactly `(LARGE_TRANSFER, ('TXN-…9001',))`.
Same transaction, opposite outcome, driven only by (c). Memo-blind: detect(strict) blank==injected.

## Open questions / blockers

- No defense AGENT chooses yet (MC-01, after the menu). Whether 3B can reason the (a)-vs-(c)
  choice is unproven → defense agent should be Option-B/policy-first (OPT-A-01b evidence).
- The `Remediation` entries are a descriptive catalog, not a uniform callable interface — that
  dispatch is MC-01's design.

## Next steps (resume here)

MC-00: write the defense-agent design contract now that the menu is genuinely >=2. Then MC-01:
the defense agent that chooses (a) vs (c) on the finding, and closes the adversarial loop
(extend `scan_guarded_agent`/`guarded_brain` per remediation; wire the Red-Team agent to re-scan
the patched target). Policy-first; LLM reasoning compute-gated.

## Handoff

- **Changed:** `core/fatf/engine.py` (+STRICT_THRESHOLDS), `core/fatf/__init__.py` (export);
  NEW `assurance/remediation.py`, `assurance/__init__.py` (exports); NEW `tests/test_remediation.py`;
  docs: ADR-0028, OPEN_QUESTIONS, feature_list KS-0620, MEMORY, this plan; `remediation_probe.md`
  committed as the design basis.
- **Unchanged (sacred):** (a) the guardrail rail, the agents' decision logic, the seam, the ledger,
  `DEFAULT_THRESHOLDS`/baseline detection, the memo-blind boundary, the schema.
- **Verified:** make check / make verify green (522 passed / 2 skipped, coverage 93.53%, pip-audit
  clean, mypy strict / Ruff / import-linter clean, AST boundary + memo-blind tests pass). PR pushed;
  NOT self-merged.
