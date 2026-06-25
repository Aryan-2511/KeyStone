# Exec-plan: UI-02 — the live-execution view (entry point) + sidebar polish

- **Slug:** `live-execution-view`
- **Feature IDs:** KS-0611 (UI-02) — done
- **Status:** done
- **Started:** 2026-06-25
- **Owner (session):** agent (Claude)

## Goal & acceptance

Make the system VISIBLY RUN: a new entry-point view where "Run the arc" reveals the five
real Layer-1 steps progressively (ledger growing entry by entry), arriving at the four
heroes as destinations. Identical reveal in live + recorded (recorded = paced real
replay, NOT instant/faked). Plus a bounded sidebar restyle ("Run the arc" the primary
action). Acceptance = KS-0611 `done_criteria`: real steps surfaced (not recomputed/faked);
the live/recorded honesty rule; sidebar to the design system; AppTest-gated; no schema
change; UI-01 + the recorded fallback not regressed.

## Context / constraints

- The 5 steps + the ledger ALREADY exist in `RunResult.arc` — SURFACE them, don't recompute
  or fake. No schema change (the arc already has the 5 entries).
- The live/recorded honesty rule is load-bearing: recorded is a PACED REAL replay, not
  instant, not a fabricated simulation.
- Keep `embed_hero` (UI-01), `components.v1.html` (not st.html), the recorded fallback.
- Sidebar polish bounded to LOOKS (no new controls). Don't restyle hero content.

## Plan

- [x] `keystone.ui.run_view`: `arc_steps(result)` (pure, the 5 real steps) + `render_run`
      (the Streamlit progressive reveal + destination cards), `RUN_RESULT_KEY`.
- [x] `keystone.ui.sidebar.style_sidebar()` — token CSS + the primary action restyle.
- [x] `run_app.py` (standalone) + integrate `run_view` as the shell's entry view (the
      destination buttons navigate via a `_pending_view` session key).
- [x] `tests/test_run_view.py` (pure: 5 real steps, real artifacts, recorded == fresh) +
      `tests/test_run_app.py` + extend `test_shell_app.py` (entry reveal + forced-break).
- [x] Verify + visual review (the revealed-state render; the reveal itself is live-only).
- [x] Docs: MEMORY / TASKS / feature_list (KS-0611 done) + the run-view screenshot.

## Progress log

- 2026-06-25 confirmed the 5 steps + ledger are in RunResult.arc — no schema change.
- 2026-06-25 built run_view (arc_steps + render_run), the shell entry integration, the
  sidebar polish; visual review (brightened the berry step labels for contrast).
- 2026-06-25 `make verify` green: 420 passed, 2 skipped; mypy strict / Ruff / import-linter
  clean, no new ignores. UI-01 + the recorded fallback + all replay paths green.

## Decisions

- **No schema change** — the five real steps + the hash-chained ledger are already in
  `RunResult.arc` (stages + entries); the view surfaces them.
- **Live/recorded = same reveal, different source** — `render_run(build, ...)`: live
  `build = build_run_result()` (computes now), recorded `build = load_run_result()` (a
  genuine saved run). Both reveal the SAME 5 paced steps. Recorded is a paced REAL replay,
  proven by a test (recorded steps == a fresh build's).
- **Kept the offline-template default for the report step** — did NOT force a live Ollama
  LLM call (that would break offline-live + the AppTest). The runner's `narrate=` supports
  a live narrator if the demo machine wants the LLM theater; the default stays offline.
- **Shell navigation via `_pending_view`** — a destination button sets a pending view key
  applied BEFORE the View radio is created next run, avoiding Streamlit's
  set-after-instantiation error.
- **Sidebar primary restyled amber→green** (not stock green) to read as THE action;
  bounded to CSS, no behaviour change. Restyleable if a different accent is preferred.

## Open questions / blockers

- None. The progressive reveal + pacing is a LOOKS/timing judgment only a live run shows
  (headless Chrome shows Streamlit's loading skeleton) — eyeball it live before merge.

## Next steps (resume here)

The demo now opens on a live run that reveals the five steps and arrives at the four
heroes. Future polish (if wanted): a tighter pace/animation; per-step timing surfaced; a
narrated four-hero walkthrough rehearsal.

## Handoff (fill in on completion)

- **Changed:** new `keystone.ui.run_view` (arc_steps + render_run), `keystone.ui.run_app`
  (standalone), `keystone.ui.sidebar` (style_sidebar); `shell_app` restructured (run view
  = entry, destinations navigate, sidebar polish); new `tests/test_run_view.py`,
  `test_run_app.py`, + 2 shell tests; docs + the run-view screenshot. **No schema/data change.**
- **Verified:** `make verify` green — 420 passed / 2 skipped; lint + mypy strict +
  import-linter clean, no new ignores. UI-01 (seamless embedding) + the recorded fallback
  + every replay path not regressed.
- **Deferred:** none.
- **Recommended next task:** the demo rehearsal / next UI or Movement task.
