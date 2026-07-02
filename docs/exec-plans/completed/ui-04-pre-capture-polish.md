# Exec-plan: UI-04 — pre-capture polish + live-run diagnosis

- **Slug:** `ui-04-pre-capture-polish`
- **Feature IDs:** KS-0615 (UI-04) — done
- **Status:** done
- **Started:** 2026-06-27
- **Owner (session):** agent (Claude)

## Goal & acceptance

Three polish items for the demo recording + DIAGNOSE the non-working "Live run" button and
resolve it HONESTLY. The run-view is the captured demo surface, so it must be clean and honest.
NO new agent logic, NO schema change. Acceptance = KS-0615 `done_criteria`: the Live control is
honest (genuinely runs / clearly says what it does — never fake-live); the agent cards dwell
longer than the stages (readable); clean page title + legible mechanism line; gates green; no
regression. Stop at green + VISUAL review (the human eyeballs the live reveal + the Live button).

## Context / constraints

- Surface: `keystone.ui.run_view` (the reveal) + `shell_app` / `run_app` (the live/recorded
  controls). The `red_team` / `triage` blocks already exist (v7) — UI-04 reads them, adds no logic.
- Honesty: a "Live run" control must EITHER genuinely run live OR clearly say it can't — NEVER
  show recorded while claiming live (fake-live, forbidden).
- Bounded to: the Live-run honesty, pacing, the page title, the mechanism-line contrast. No
  other restyle. No regression to UI-01/02/03 or the recorded fallback (the capture surface).

## Plan

- [x] Step 0: base — UI-03 merged to main (PR #37, after asking the user); branched
      `ui-04-pre-capture-polish`; `make verify` green on the base.
- [x] Part A: diagnose the Live button (trace what it calls; confirm/refute the Ollama/Garak
      hypothesis) → REFUTED; resolve honestly (the label).
- [x] Part B: pacing — `STEP_PACE` 0.35→0.6; the agent cards a longer `AGENT_DWELL` (1.6s).
- [x] Part C: page title → "Keystone" (shell_app + run_app); mechanism line MUTED → TEXT_DIM.
- [x] Tests: live mode renders the honest framing; agent cards dwell longer than stages.
- [x] Verify: `make check` + `make verify` green; preview regenerated.
- [x] Docs: feature_list (KS-0615), TASKS, MEMORY, this exec-plan.

## Progress log

- 2026-06-27 base: UI-03 not in main → asked the user → they merged (PR #37); branched; base
  verify green.
- 2026-06-27 Part A: timed `build_run_result()` with sockets blocked → OK in 0.04s, NO network;
  AppTest live path renders the full reveal, no exception → hypothesis REFUTED. Confirmed the
  agent blocks are identical live vs recorded (`test_recorded_*_block_equals_a_fresh_build`).
- 2026-06-27 implemented honest live label + pacing + title + contrast; tests added; green.
- 2026-06-27 `make check` (460) + `make verify` (469) green; preview regenerated; commits.

## Decisions

- **Part A — the Live button is NOT broken; the hypothesis is REFUTED.** `build_run_result()`
  is fully offline (template narrative + the recorded defense profile for the agents); it needs
  no Ollama/Garak and runs in ~0.04s. The genuine issue was honesty: the label over-implied a
  live AGENT run while the agents replay the recorded profile identically in both modes.
  **Resolution:** make the label honest (live recomputes the arc offline; the agents replay the
  recorded profile; not fake-live) and KEEP it enabled — it genuinely works. Did NOT disable it
  (disabling a working control would be dishonest in the other direction); did NOT fake-live.
- **Part B — agent cards dwell longer** (`AGENT_DWELL` > `STEP_PACE`, mechanically tested) —
  they carry the most text and are the moments being sold; the deterministic stages are one line.
- **Part C — title + contrast** — page title "Keystone"; the mechanism/honesty line bumped from
  the dim `MUTED` to the legible `TEXT_DIM` (token-driven), still set apart by the italic mono.
- **Scope held** — did NOT touch the sidebar `*` font CSS or add speculative Material-icon CSS
  (out of the bounded scope, and I can't verify the render headlessly). If a `keyboard_double_…`
  ligature persists it's the Streamlit sidebar-collapse icon, flagged for the human to confirm.

## Open questions / blockers

- The browser extension wasn't connected, so I couldn't auto-screenshot or click the live
  button in a real browser; AppTest (the faithful script runner) proves the live path renders
  with no exception, and the offline timing proves no network. The reveal/pacing + any residual
  Material-icon artifact need the human's live eyeball (headless shows the skeleton).

## Next steps (resume here)

- **Demo capture + the deck**: the run-view is now clean + honest + readably paced — capture
  the recorded reveal for the deck; if the live button is shown, the honest label covers it.
- Optional: if the `keyboard_double_arrow` Material-icon ligature shows in the capture, fix the
  Streamlit sidebar-collapse icon font (verify the selector against the live DOM first).

## Handoff

- **Changed:** `keystone.ui.run_view` (pacing constants `STEP_PACE`/`AGENT_DWELL` + longer agent
  dwell; mechanism line MUTED→TEXT_DIM); `keystone.ui.shell_app` + `run_app` (page title
  "Keystone"; honest Live-run label + data-source help); `tests/test_run_view.py` (pacing
  intent) + `tests/test_run_app.py` (honest live framing); docs (feature_list KS-0615 / TASKS /
  MEMORY / this plan). NO new agent logic, NO schema change.
- **Verified:** `make check` (460) + `make verify` (469 passed, 2 skipped, 93.4% coverage)
  green; mypy strict / Ruff / import-linter clean, no new ignores. All replay paths + the
  recorded fallback green; offline intact; UI-01/02/03 not regressed.
- **Deferred:** the Material-icon ligature (if it shows live); a dedicated agentic hero/screen;
  wiring genuine live Garak/Ollama agent execution (Option A territory).
- **Recommended next task:** demo capture + the deck.
