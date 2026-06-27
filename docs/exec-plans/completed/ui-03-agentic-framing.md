# Exec-plan: UI-03 — agentic framing pass (foreground the two real agents)

- **Slug:** `ui-03-agentic-framing`
- **Feature IDs:** KS-0614 (UI-03) — done
- **Status:** done
- **Started:** 2026-06-27
- **Owner (session):** agent (Claude)

## Goal & acceptance

The system is now genuinely multi-agent (Red-Team MA-01 + Triage MB-01). The run-view
(UI-02) still labelled everything as neutral workflow stages — it UNDER-claimed. Make the
run-view honestly FOREGROUND the two agents at the two moments they genuinely act, while
keeping the deterministic stages honest as stages. FRAMING of EXISTING behavior — NO new
agent capability, NO new logic, NO schema change (reads the existing red_team/triage blocks).
Serves the deck demo capture. Acceptance = KS-0614 `done_criteria`: the two moments read the
real blocks (not hardcoded); honest policy-not-LLM framing; the supervisor-worker link
visible; the deterministic stages stay honest stages, visibly distinct; AppTest green; gates
green. Stop at green + VISUAL review (human eyeballs the running app).

## Context / constraints

- The surface is `keystone.ui.run_view` (UI-02's progressive 5-step reveal); `RunResult`
  already carries `red_team` (v6) + `triage` (v7) — the agents' real decisions. The framing
  READS those; it does NOT recompute or add agent logic.
- Honesty: show what the agents ACTUALLY do (adaptive selection; interplay routing), framed
  as adaptive POLICY not LLM; recorded mode replays REAL decisions (don't imply live-on-stage).
- Do NOT relabel deterministic stages as agents (the Path A lesson — the contrast is the
  story). No new hero/screen (deferred). No regression to UI-01/UI-02/the recorded fallback.

## Plan

- [x] Step -1: disk check (18 G free — OK).
- [x] Step 0: base — MB-01 merged to main (PR #36); branched `ui-03-agentic-framing`;
      `make verify` green on the base.
- [x] `keystone.ui.run_view`: `RedTeamMoment` / `TriageMoment` dataclasses + pure derivations
      `red_team_moment` / `triage_moment` (read the blocks); `_agent_block` (the distinct card)
      + `_red_team_card` / `_triage_card`; interleave the two moments into `render_run`'s
      reveal (Red-Team after DETECT, Triage after SEAM-BIND); honest header tweak.
- [x] Tests: `test_run_view.py` — the moments read the real blocks (not hardcoded), the
      worker-link, recorded==fresh; `test_run_app.py` — both moments render in the running app.
- [x] Verify: `make check` + `make verify` green; standalone-HTML preview generated.
- [x] Docs: feature_list (KS-0614), TASKS, MEMORY, this exec-plan.

## Progress log

- 2026-06-27 disk 18 G; base (MB-01 in main) confirmed; `make verify` green on base; branch.
- 2026-06-27 built the two moment derivations + the distinct agent cards + the interleave;
  ruff PLR0913 fixed by folding accent+wash into a `colors` tuple (no noqa); ruff-format pass.
- 2026-06-27 tests green (run_view + run_app + shell_app); `make check` (459) green; preview
  HTML written; verified the moments read real data (latentinjection 83% / ESCALATE).
- 2026-06-27 `make check` + `make verify` green; code commit; docs updated.

## Decisions

- **Interleave, don't replace** — the 5 deterministic stage cards (and `arc_steps` + the
  ledger 1→5 count) are UNCHANGED; the two agent moments are inserted between them. So UI-02's
  tests/behavior are untouched and the contrast is structural.
- **Distinct card styling = the contrast** — stage cards: flat panel, green ✓, ledger N/5.
  Agent cards: tinted boxed card, accent ◆, an `AGENT` tag, NO ledger count, + the honest
  `mechanism` line. The reasoning-vs-determinism contrast is visible (the Path A lesson).
- **Placement** — Red-Team after DETECT (the offense that found the L2 vuln seam-bind then
  references); Triage after SEAM-BIND (it routes the now-bound finding). Coherent, honest flow.
- **Reads the blocks, surfaces the worker link** — `red_team_moment`/`triage_moment` are pure
  functions of the RunResult; `reads_red_team_exploit` marks that Triage's `failure_rate` IS
  the Red-Team Agent's landed exploit (the literal supervisor-worker topology).
- **No schema change** — the blocks already exist at v7; this is presentation only.

## Open questions / blockers

- None. The browser extension wasn't connected, so I couldn't auto-screenshot; a
  standalone-HTML preview proves the design and the AppTest proves the app renders the moments.
  Per the M1-06 finding, the live progressive reveal must be eyeballed live (headless shows
  the skeleton) — the human does the visual gate before merge.

## Next steps (resume here)

- **Demo capture + the deck**: now that the run-view foregrounds the two agents, capture the
  reveal (live) for the deck; update the deck narrative to the now-true "multi-agent system"
  present-tense claim.
- Optional later: a dedicated agentic hero/screen (the deferred larger version); Option A
  upgrades (LLM-reasoned agents); surface MA-01's offline-characterization caveat in a
  reachable expander if a reviewer asks.

## Handoff

- **Changed:** `keystone.ui.run_view` (the two `*Moment` dataclasses + `red_team_moment` /
  `triage_moment` derivations + `_agent_block` / `_red_team_card` / `_triage_card` + the
  interleave in `render_run` + an honest header line); `tests/test_run_view.py` (the moments
  read the real blocks) + `tests/test_run_app.py` (both moments render); docs
  (feature_list KS-0614 / TASKS / MEMORY / this plan). NO schema change, NO new agent logic.
- **Verified:** `make check` (459) + `make verify` green; mypy strict / Ruff / import-linter
  clean, no new ignores. All replay paths + the recorded fallback green; offline intact;
  UI-01/UI-02 not regressed. Standalone preview: the Red-Team moment shows the real adaptive
  trace (latentinjection 83% landed, promptinject abandoned); the Triage moment shows the real
  route (ESCALATE) over 83%/clean/HIGH, with the worker link.
- **Deferred:** a dedicated agentic hero/screen; the live demo capture + deck update; Option A.
- **Recommended next task:** demo capture + the deck (the multi-agent claim is now true and
  visible in the run-view).
