# Exec-plan: MB-01 — the Triage Agent (supervisory triage policy)

- **Slug:** `mb-01-triage-agent`
- **Feature IDs:** KS-0613 (MB-01) — done
- **Status:** done
- **Started:** 2026-06-26
- **Owner (session):** agent (Claude)

## Goal & acceptance

Build Keystone's SECOND genuine agent: a SUPERVISORY triage agent that routes a security
finding three ways — remediate / accept / escalate — by reasoning over the INTERPLAY of
its already-computed signals (failure_rate, seam_result, severity), NOT a single threshold.
Ship **Option B — an adaptive triage policy** (MB-00 §3), framed honestly (not an LLM).
Acceptance = KS-0613 `done_criteria` + `MB-00_TRIAGE_AGENT_DESIGN.md`: the §2 interplay
honesty test passes (same rate, different seam → different route); all three routes
reachable; record/replay at schema v7 (recorded==fresh, all replay paths green); the
memo-blind boundary holds with BOTH agents present. With MA-01, Keystone is now MULTI-AGENT.

## Context / constraints

- Agent lives in `keystone.agents` alongside `red_team` (two agents, one package — the
  multi-agent system). Imports nothing on the detection path (the boundary is stricter than
  import-linter, enforced by an AST scan).
- The three signals are already-computed and read-only: `failure_rate` (the offense
  worker's ProbeOutcome/GarakFinding rate), `seam_result` ∈ CLEAN/BOUNDARY/OPEN
  (`framework.SeamResult`), `severity` ∈ LOW/MEDIUM/HIGH (`fatf.models.Severity`).
- Step 1 (the interplay must be REAL): confirmed ≥1 (rate, seam) combination where the same
  rate routes differently by seam — not illusory. CLEAN and BOUNDARY both occur in
  REGISTERED_PAIRS; the interplay is semantic (a high attack rate on a CLEAN bind is a real
  vuln → remediate; the same on a provably-non-binding BOUNDARY is contained → accept).
- Record/replay (MB-00 §4): the triage decision is DERIVED by running the agent over signals
  the runner hands it. The supervisor-over-worker topology is literal (the rate it reads IS
  the Red-Team Agent's headline exploit).
- The memo-blind boundary (MB-00 §4, SACRED): the supervisor reads only signals; never the
  detector / attack channel. The 4 independence locks hold with BOTH agents present.
- No LLM-reasoned triage (Option A is later); "remediate" is a ROUTE not a fix-selection
  (Movement C); no NAT-native/LangChain deps; the deterministic core + matrix are untouched.

## Plan

- [x] Step -1: disk check (19 G free > ~10 G threshold — OK to proceed).
- [x] Step 0: base — MA-01 was unmerged on its branch; per the user, merged MA-01 to main
      (PR #35) first, then branched `mb-01-triage-agent` off the updated main. `make verify`
      green on the base.
- [x] Step 1: confirmed the interplay is REAL (same rate, different seam → different route;
      CLEAN/BOUNDARY genuine, severity HIGH genuine).
- [x] `keystone.agents.triage`: `Route`/`SeamClassification`/`FindingSeverity` (own value
      enums), `TriageSignals`, `ACTION_FLOOR`, `route_for` (the policy), `triage`,
      `TriageDecision`, `MECHANISM`.
- [x] `tests/test_triage_agent.py` — THE §2 interplay test + all-routes + determinism +
      parity locks. `tests/test_triage_boundary.py` — the AST import-scan + both-agents locks.
- [x] Schema v6→v7 (own commit): `RunResult.triage` (`TriageView`),
      `demo.triage.build_triage_view`, wire into runner, regenerate `recorded_run.json` as a
      genuine run, migrate `test_offline_fallback`, add `triage` block tests.
- [x] Verify: `make check` + `make verify` green.
- [x] Docs: feature_list (KS-0613), TASKS, ROADMAP, MEMORY, this exec-plan.

## Progress log

- 2026-06-26 disk check 19 G free; MA-01 found unmerged → user chose "merge MA-01 first";
  merged PR #35; branched `mb-01-triage-agent` off main; base `make verify` green (439).
- 2026-06-26 confirmed the signal sources + Step-1 interplay reality; committed MB-00 design
  doc (6ee551e); built the agent; agent + boundary tests green (21 passed); agent commit
  (2da220e).
- 2026-06-26 schema v6→v7 + `triage` block; recorded_run.json regenerated; recorded==fresh;
  all replay paths green (177 in the targeted set); schema commit (78f3f80); a small mypy
  guard for `module.__file__` in the boundary scan.
- 2026-06-26 `make check` (455) + `make verify` (464) green; docs updated.

## Decisions

- **Option B (adaptive triage policy), framed honestly** — `MECHANISM` says "…not an LLM".
  An agent by the §2 bar (the route depends on the observed combination, ≥2 genuine options)
  but it reasons via an explicit policy. Option A (LLM-reasoned) is a later upgrade.
- **The policy = severity-then-floor-then-seam** — HIGH severity → escalate (regardless of
  rate); else below ACTION_FLOOR=0.10 → accept; else the seam context decides (OPEN →
  escalate, BOUNDARY → accept, CLEAN → remediate). The route is a pure fn of the combination,
  so the same rate flips by seam — the §2 interplay proof.
- **The agent carries its OWN value enums** (`SeamClassification`, `FindingSeverity`) instead
  of importing `framework.SeamResult` / `fatf.Severity` — so it imports nothing on the
  detection path (the boundary is structural). A parity test pins the values so they can't
  drift; the demo/triage.py translation layer (allowed to import both) maps real→agent.
- **The supervisor reads the worker's output** — `failure_rate` = the Red-Team Agent's
  strongest landed exploit on the run (the supervisor-worker topology made literal). The
  hero finding (0.833, CLEAN, HIGH) routes to ESCALATE on this run.
- **Schema v7, own commit before dependents** (the v2 lesson) — the `triage` block is DERIVED
  by actually running the agent; recorded_run.json regenerated as a genuine run; recorded==
  fresh asserted.
- **Boundary enforced structurally** — an AST import-scan asserts the triage agent imports
  nothing on the detection path / attack channel; the 4 independence locks hold with BOTH
  agents present.

## Open questions / blockers

- None. OPEN is a documented seam result not currently produced by any REGISTERED_PAIR; the
  agent handles it for completeness (escalate), and the interplay is also proven on the
  genuinely-occurring CLEAN vs BOUNDARY pair — so the proof is grounded, not theater.

## Next steps (resume here)

- **Movement C** (gated): a Defense Agent that CHOOSES among a real ≥2-remediation menu →
  the adversarial offense↔defense loop. Only when the menu is genuinely ≥2 distinguishable
  options (else agency-theater).
- Optional: Option A upgrades (LLM-reasoned red-team / triage, recorded/replayed); a UI
  surface for the `triage` decision; an agentic-framing pass on the deck + demo now that the
  multi-agent claim is true.

## Handoff

- **Changed:** new `keystone.agents.triage` (the agent) + `keystone.agents.__init__` exports
  (incl. `TRIAGE_MECHANISM`); new `keystone.demo.triage` (`build_triage_view`);
  `RunResult.triage` (schema v7) + runner wiring + demo exports; `recorded_run.json`
  regenerated (v7); new `tests/test_triage_agent.py` (the §2 interplay test) +
  `tests/test_triage_boundary.py` + `triage` block tests in `test_demo_run_result.py`;
  `test_offline_fallback` pinned to v7; the MB-00 design doc committed at root; docs
  (feature_list/TASKS/ROADMAP/MEMORY).
- **Verified:** `make check` (455) + `make verify` (464) green; mypy strict / Ruff /
  import-linter clean, no new ignores. recorded==fresh at v7; every replay path (seam,
  jurisdiction, matrix, convergence, run-view, red_team) green; hash chain re-verifies;
  offline-default intact. The boundary holds with BOTH agents present.
- **Deferred:** Option A (LLM-reasoned triage); Movement C (the Defense Agent); a UI for the
  trace; the agentic-framing pass on the deck/demo.
- **Recommended next task:** the agentic-framing pass (deck + demo) now that "multi-agent" is
  true, or Movement C when a real ≥2-remediation menu exists.
