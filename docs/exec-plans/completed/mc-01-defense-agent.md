# Exec-plan: MC-01 — the Defense Agent (finding-dependent remediation choice)

- **Slug:** `mc-01-defense-agent`
- **Feature IDs:** KS-0621 (Movement C; contract MC-00_DEFENSE_AGENT_DESIGN.md)
- **Status:** done (PR pushed, awaiting review — not self-merged)
- **Started:** 2026-07-06
- **Owner (session):** Claude (Opus 4.8)

## Goal & acceptance

Build Keystone's THIRD agent: a Defense Agent that CHOOSES which remediation a finding warrants
— (a) block the AI side vs (c) tighten the money side — via a uniform interface, policy-first
(OPT-A-01b: 3B can't reason this reliably). Gated by a built-in Phase-0 probe that PROVES the
choice is genuinely finding-dependent (else theater → STOP). MC-01 STOPS at applying the
remediation (the loop is MC-02). Memo-blind sacred. Acceptance = KS-0621 done_criteria.

## Plan

- [x] Step 0: base clean (main @ 92b5866, MC-PRE-01 merged); baseline verify green (522).
      First commit: `MC-00_DEFENSE_AGENT_DESIGN.md` — the USER'S authored design doc (found
      untracked at repo root, where the other design docs live: MA-00 / MB-00 / OPTION-A-00);
      committed it as the design basis. My implementation matches its §2 (uniform apply) / §3
      (the flip) contract and resolves its §8 open items. (A redundant draft I wrote in `docs/`
      was removed.)
- [x] **Phase 0 GATE (passed):** proved from real data that findings carry INDEPENDENT two-sided
      strength (AI-side failure_rate vs financial-side gap) that is not correlated → the choice flips.
- [x] Phase 1: uniform interface — `Remediation.apply(context) -> RemediationOutcome`
      (`assurance.remediation`); (a) and (c) implement it; `side`/`verified_offline`/`retest_via`.
- [x] Phase 2: the agent — `keystone.agents.defense.defend` (policy, memo-blind); recorded on
      `RunResult.defense` (optional field, NO bump); demo/runner/narrate wired; recorded_run regenerated.
- [x] Honesty tests: flip, both-reachable, determinism, memo-blind, uniform interface
      (`test_defense_agent.py`); boundary (`test_defense_boundary.py`, all 3 agents present).
- [x] Gates: make check / make verify green (538 passed, 2 skipped); mypy/Ruff/import-linter clean.
- [x] Docs: ADR-0029, OPEN_QUESTIONS, feature_list KS-0621, MEMORY, ROADMAP, TASKS, CLAUDE, this plan.

## Phase-0 probe result (the gate)

- **Independence real:** AI-side `failure_rate` = Garak scan of model susceptibility (runner.py);
  financial-side `financial_gap` = FATF coverage baseline-vs-strict (memo-blind, `financial_detection_gap`).
  Different subsystems, different aspects.
- **Not correlated:** the real demo finding is `failure_rate 0.92` with `financial_gap False`
  (strong-AI / no-gap); the lone-9,000 tx is low-rate with `financial_gap True` (weak-AI / strong-fin).
- **Both discriminating findings exist in real data** → decision space is real → BUILD (not theater).

## Decisions

- **Policy:** `(c) iff (financial_gap and failure_rate < 0.10)`, else `(a)`. Both signals matter
  ((c) needs the conjunction); (a) is the root-cause/default control. Genuine flip, both reachable.
- **Uniform interface, honest asymmetry:** `verified_offline` is bool for (c) (offline detection
  change, verifiable now) / None for (a) (needs the MC-02 re-scan); `retest_via` loop-ready.
- **No schema bump:** `defense: DefenseView | None = None` — old runs load (mirrors OPT-A-01/02).
- **Defense is not a pure supervisor like Triage:** it dispatches remediations (imports
  `assurance.remediation`), but its CHOICE is memo-blind and it reaches no attack channel /
  detector-lock directly — a defense-specific boundary test pins the correct invariant.

## THE FLIP (proof)

- (a)-favoring (failure_rate 0.90, gap False) → **(a) `nemo-guardrails-input-rail`** ("injection
  live → close the AI hole").
- (c)-favoring (failure_rate 0.03, gap True) → **(c) `fatf-strict-thresholds`** ("injection
  contained but money slipping → tighten"), applied: `verified_offline=True`, `detail=(TXN-009001,)`.
- Same finding → same choice; both reachable; determinism holds. The demo finding chooses (a).

## Open questions / next steps

- **MC-02** — the adversarial loop: re-scan the patched target (extend
  `scan_guarded_agent`/`guarded_brain` per remediation) and let the Red-Team agent adapt. The
  `retest_via` handle is built for it; not wired here.
- LLM-reasoned remediation choice stays compute-gated (OPT-A-01b); the policy is the honest default.

## Handoff

- **Changed:** NEW `agents/defense.py`, `demo/defense.py`, `tests/test_defense_agent.py`,
  `tests/test_defense_boundary.py`, `MC-00_DEFENSE_AGENT_DESIGN.md` (the user's, committed);
  `assurance/remediation.py`
  (uniform interface), `assurance/__init__.py`, `agents/__init__.py`, `demo/run_result.py`
  (DefenseView + optional field), `demo/__init__.py`, `demo/runner.py`, `demo/narrate.py`,
  `recorded_run.json`; docs: DECISIONS ADR-0029, OPEN_QUESTIONS, feature_list KS-0621, MEMORY,
  ROADMAP, TASKS, CLAUDE, this plan.
- **Unchanged (sacred):** (a)/the rail, Red-Team & Triage decision logic, the seam, the FATF
  baseline, the ledger, the memo-blind boundary; no schema bump.
- **Verified:** make check / make verify green (538 passed / 2 skipped, mypy/Ruff/import-linter
  clean, AST boundary + all-three-agents independence pass). PR pushed; NOT self-merged.
