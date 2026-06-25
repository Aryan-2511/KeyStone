# Exec-plan: MA-01 — the Red-Team Agent (adaptive offensive policy)

- **Slug:** `ma-01-redteam-agent`
- **Feature IDs:** KS-0612 (MA-01) — done
- **Status:** done
- **Started:** 2026-06-26
- **Owner (session):** agent (Claude)

## Goal & acceptance

Build Keystone's FIRST genuine agent: an OFFENSIVE red-team agent that observes the
outcome of each prompt-injection probe it fires and ADAPTS its next choice over the
23-probe Garak prompt-injection space. Ship **Option B — an adaptive offensive
policy** (MA-00 §3), framed honestly (not an LLM agent). Acceptance = KS-0612
`done_criteria` + `MA-00_REDTEAM_AGENT_DESIGN.md`: the §2 honesty test passes (flip
observations → the probe sequence flips); a real ≥2-family / ≥2-probe decision space;
record/replay at schema v6 (recorded==fresh, all replay paths green); the memo-blind
boundary holds with the agent in the loop.

## Context / constraints

- Agent lives in `keystone.agents` (Path A kept the name as a forward-promise — MA-01
  makes it true). Edge→edge import of `keystone.assurance.garak_probe` is allowed
  (import-linter only forbids core→edge).
- The decision space is the 23 in-family probes (`latentinjection` ×17, `promptinject`
  ×6), selectable via `ScanConfig.probes`/`--probes` — confirmed live via
  `garak --list_probes` (v0.15.1).
- Record/replay (MA-00 §4): `observe` injected — live = real Garak; offline = a
  deterministic profile. The recorded run must be a faithful capture of a genuine run.
- The memo-blind boundary (MA-00 §5, SACRED): the agent is offense-side and must NEVER
  reach the detector. The 4 lock points must not loosen.
- No LLM-reasoned selection (Option A is later); no NAT-native/LangChain deps; the
  deterministic core's behaviour and the Movement-1 matrix are untouched.

## Plan

- [x] Step -1: disk check (21 G free > ~10 G threshold — OK to proceed).
- [x] Step 0: clean base (main @ 05212d3, Path A merged), branch `ma-01-redteam-agent`,
      commit the three design docs (resolve the dangling Path-A pointers).
- [x] `keystone.agents.red_team`: `PROBE_CATALOG`, `choose_next` (the policy),
      `run_red_team`, `ProbeOutcome`/`RedTeamDecision`/`RedTeamTrace`, `garak_observe`
      (live) + `profile_observe` (offline) + `RECORDED_DEFENSE_PROFILE`.
- [x] `tests/test_red_team_agent.py` — THE §2 honesty test + agency-bar structure +
      a `-m slow` live path. `tests/test_red_team_boundary.py` — the memo-blind locks.
- [x] Schema v5→v6 (own commit): `RunResult.red_team` (`RedTeamView`),
      `demo.red_team.build_red_team_view`, wire into runner, regenerate
      `recorded_run.json` as a genuine run, migrate `test_offline_fallback`.
- [x] Verify: `make check` + `make verify` green.
- [x] Docs: feature_list (KS-0612), TASKS, ROADMAP, MEMORY, this exec-plan.

## Progress log

- 2026-06-26 disk check 21 G free; base confirmed (Path A in main, PR #34); branch +
  design-docs commit (d7ebf7a).
- 2026-06-26 confirmed the 23-probe surface live (`garak --list_probes`); built the
  agent; smoke-tested the flip (S1 escalates latentinjection / S2 flips to promptinject).
- 2026-06-26 honesty + boundary tests green (16 passed); agent commit (84d6473).
- 2026-06-26 schema v5→v6 + `red_team` block; recorded_run.json regenerated; recorded==
  fresh; full fast suite 428 passed; schema commit (5ba84ee).
- 2026-06-26 `make check` + `make verify` green; docs updated.

## Decisions

- **Option B (adaptive offensive policy), framed honestly** — `MECHANISM` says "…not an
  LLM". It is an agent by the §2 bar (next action depends on observation) but reasons via
  an explicit policy. Option A (LLM-reasoned) is a later upgrade; never claim A while
  shipping B.
- **Policy = scout-then-exploit** — one lead probe per family (scout), then escalate the
  family getting through hardest (`failure_rate`), abandon families fully blocked, stop if
  nothing gets through. The full sequence is a pure function of observations, so it flips.
- **`observe` is injected** — `garak_observe` (live Garak) vs `profile_observe` (offline
  deterministic profile). The offline `RECORDED_DEFENSE_PROFILE` anchors the latentinjection
  lead to the REAL captured fixture (10/12); the rest is a documented characterization.
- **Schema v6, own commit before dependents** (the v2 lesson) — the `red_team` block is
  DERIVED by actually running the agent (mirrors matrix/convergence); recorded_run.json
  regenerated as a genuine run; recorded==fresh asserted.
- **Boundary enforced structurally** — the agent imports nothing on the detection path; an
  AST import-scan test asserts it, and the 4 independence locks hold with the agent present.

## Open questions / blockers

- None. The live adaptive path (`garak_observe`) is exercised by a `-m slow` test that
  skips cleanly when garak/Ollama are unavailable; the AppTest/replay gate runs against the
  recorded trace offline.

## Next steps (resume here)

- **Movement B — the Triage Agent (`MB`)**: the second agent (route remediate / accept /
  escalate over already-observable state). Two genuine agents = a multi-agent system —
  claimed only once MB lands.
- Optional later: Option A (LLM-reasoned selection on a capable model, recorded/replayed);
  a UI surface for the `red_team` decision trace.

## Handoff

- **Changed:** new `keystone.agents.red_team` (the agent) + `keystone.agents.__init__`
  exports; new `keystone.demo.red_team` (`build_red_team_view`); `RunResult.red_team`
  (schema v6) + runner wiring + demo exports; `recorded_run.json` regenerated (v6); new
  `tests/test_red_team_agent.py` (the §2 honesty test) + `tests/test_red_team_boundary.py`
  + a `red_team` block test in `test_demo_run_result.py`; `test_offline_fallback` pinned to
  v6; the three design docs committed at root; docs (feature_list/TASKS/ROADMAP/MEMORY).
- **Verified:** `make check` + `make verify` green; mypy strict / Ruff / import-linter
  clean, no new ignores. recorded==fresh at v6; every replay path (seam, jurisdiction,
  matrix, convergence, run-view) green; hash chain re-verifies; offline-default intact.
- **Deferred:** Option A (LLM-reasoned selection); the Triage Agent (MB); a UI for the trace.
- **Recommended next task:** Movement B — the Triage Agent.
