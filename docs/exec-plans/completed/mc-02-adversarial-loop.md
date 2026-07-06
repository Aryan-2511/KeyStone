# Exec-plan: MC-02 — Close the adversarial loop (offense→defense→re-scan→adapt)

- **Slug:** `mc-02-adversarial-loop`
- **Feature IDs:** KS-0622 (Movement C finale; contract MC-00_DEFENSE_AGENT_DESIGN.md §4)
- **Status:** done (PR pushed, awaiting review — not self-merged)
- **Started:** 2026-07-06
- **Owner (session):** Claude (Opus 4.8)

## Goal & acceptance

Close Movement C's offense↔defense loop: after the Defense Agent (MC-01) patches, the Red-Team
RE-SCANS the PATCHED target and ADAPTS. Generalize the re-scan (hard-wired to the one rail /
unguarded target) to the patched target. Offline default (recorded), live opt-in (real Garak,
OPT-A-02b cost discipline). Handle (a) real-re-scan vs (c) offline-re-verify honestly. MEASURE
the patch (don't assume). Memo-blind sacred. Acceptance = KS-0622 done_criteria.

## Plan

- [x] Step 0: base clean (main @ 49f4b09, MC-01 merged); garak 0.15.1 up; baseline verify green (522).
- [x] `keystone.agents.adversarial`: RECORDED_GUARDED_PROFILE (anchored to REFERENCED_ASSURANCE),
      guarded_observe (live re-scan; importlib-lazy garak_endpoint → offline stays lean),
      close_loop (a: real re-scan + adapt; c: offline re-verify).
- [x] Record on RunResult.adversarial_loop (optional field, NO bump); demo/adversarial.py builder;
      runner captures raw trace+decision once (project_red_team_view / defense_decision) + closes loop;
      narrate finale (4c); recorded_run regenerated.
- [x] Tests: before/after-patch proof, adapt (held/pivot), (c) re-verify, honest not-mitigated,
      offline-exercisable, memo-blind AST, slow live re-scan. All green.
- [x] Gates: make check / make verify green (547 passed, 2 skipped). Live proof measured.
- [x] Docs: ADR-0030, OPEN_QUESTIONS (MC complete), feature_list KS-0622, MEMORY, ROADMAP, TASKS,
      CLAUDE (complete multi-agent system), this plan.

## Decisions

- **Recorded post-patch = injection blocked (0), anchored to REFERENCED_ASSURANCE** (KS-0304:
  10/12→0/12), the rail being a general memo-injection rail. Non-lead probes modeled from the
  rail design (not separately captured); the live re-scan measures the exploited probe. Honest.
- **The adaptation re-run is deterministic over the recorded guarded posture** (not per-probe
  live) → a live loop makes exactly ONE real guarded scan (the exploited probe). Tractable.
- **(a) real re-scan vs (c) offline re-verify** — different `kind`/`source`; (c) is NEVER claimed
  as a live post-patch scan.
- **Offline stays lean:** garak_endpoint (→ nemoguardrails) is loaded via `importlib` inside
  guarded_observe's closure; a test confirms nemoguardrails is not imported in an offline build.
- **No schema bump:** `adversarial_loop: AdversarialLoopView | None = None` (mirrors defense).
- **`mitigated` is MEASURED**; the "patch didn't mitigate" branch is a first-class honest outcome.

## THE PROOF (loop closed, before/after-patch)

- Recorded: latent lead **11/12** (unpatched) → (a) applied → re-scan patched → **0/12** →
  mitigated=True; Red-Team re-runs, surface closed, `adapted_exploited_family=None` (defense held).
- Measured LIVE (real Garak of the guarded endpoint): **11/12 → 0/4**, `source=garak_live`,
  mitigated=True.
- Adaptation mechanism also proven: partial patch (only latent closed) → Red-Team **pivots** to
  promptinject; general rail (surface closed) → Red-Team **abandons** (defense held).

## Open questions / next steps

- **Movement C is COMPLETE.** Remaining frontier: LLM-reasoning for all three agents' decisions
  (compute-gated, OPT-A-01b) — the purpose-fine-tuned small on-prem model (the NVIDIA ask).

## Handoff

- **Changed:** NEW `agents/adversarial.py`, `demo/adversarial.py`, `tests/test_adversarial_loop.py`;
  `agents/__init__.py`, `demo/__init__.py`, `demo/run_result.py` (AdversarialLoopView + optional
  field), `demo/runner.py` (raw trace+decision, loop wiring), `demo/red_team.py`
  (red_team_trace / project_red_team_view), `demo/defense.py` (defense_decision /
  project_defense_view), `demo/narrate.py` (4c finale), `recorded_run.json`; docs: DECISIONS
  ADR-0030, OPEN_QUESTIONS, feature_list KS-0622, MEMORY, ROADMAP, TASKS, CLAUDE, this plan.
- **Unchanged (sacred):** the agents' core decision logic (choose_next, triage routing,
  choose_remediation), (a)/(c) core behaviour, the seam, the FATF baseline, the ledger, the
  memo-blind boundary; no LLM in the loop; offline/recorded default; no schema bump.
- **Verified:** make check / make verify green (547 passed / 2 skipped, mypy/Ruff/import-linter
  clean, AST boundary passes, offline stays lean, live re-scan measured). PR pushed; NOT self-merged.
