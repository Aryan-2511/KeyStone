# Exec-plan: M2-0n — the convergence hero (the loop made visible)

- **Slug:** `convergence-hero`
- **Feature IDs:** KS-0609 (M2-0n) — done. **Movement 2 COMPLETE.**
- **Status:** done
- **Started:** 2026-06-24
- **Owner (session):** agent (Claude)

## Goal & acceptance

Movement 2's payoff screen: surface the evidence mappings in the RunResult (schema bump,
derived from REGISTERED_MAPPINGS), build the temporal state-flip hero ("The same event.
Violated, then satisfied."), ship its AppTest gate, host it in the shell as the fourth
hero. Acceptance = KS-0609 `done_criteria`: the convergence block is derived at the new
schema with every replay path green; the hero renders the state-flip with the before/after
as cause, the cross-jurisdiction spread, the DPDP boundary as a deliberate result, and the
disclaimer on screen; AppTest-gated and shell-hosted.

## Context / constraints

- Schema+UI lessons (M1-06): components.v1.html (not st.html); ship the AppTest; a bump
  must migrate every fixture and keep all FOUR replay paths green (now at 4-screen stakes).
- Derive from REGISTERED_MAPPINGS (single source). The DPDP boundary is a deliberate
  result, never empty. The before/after-as-cause = the 10→0 IS the violated→satisfied flip.
- The EVIDENCE_DISCLAIMER on the screen (a credibility asset, not a hedge).

## Plan

- [x] **Part A (own commit):** RunResult v5 — `convergence` block
      (`ConvergenceView`/`ConvergenceMappingView`) via `demo.convergence.build_convergence_view`
      from REGISTERED_MAPPINGS; migrate `recorded_run.json`; round-trip + chain re-verify;
      all four replay paths green. Landed first.
- [x] **Part B:** `ui.convergence_screen` (temporal state-flip: centre VIOLATED→SATISFIED
      with 10→0 as cause; one-deep-rest-compact strip; DPDP dashed boundary; disclaimer
      footer) + `convergence_app`. Visual review via headless-Chrome screenshot.
- [x] **Part C:** AppTest (`test_convergence_app`: live + replay + forced-break) + screen
      unit tests (`test_convergence_screen`: derived, state-matches-derived, boundary,
      disclaimer, tokens, empty); plug into `shell_app` as the 4th hero (views → ⑦); shell
      AppTest green.
- [x] Verify: `make check && make verify` green; visual review of the running figure.
- [x] Docs: MEMORY / TASKS / ROADMAP / feature_list (KS-0609 done) + screenshot asset.

## Progress log

- 2026-06-24 Part A: v5 convergence block derived from REGISTERED_MAPPINGS; fixture
  regenerated; all four replay paths green. Committed separately.
- 2026-06-24 Part B/C: built the state-flip hero; visual review (fixed the summary/headline
  overlap and the boundary-card overflow); AppTest + screen tests; hosted in the shell.
- 2026-06-24 `make verify` green: 410 passed, 2 skipped; mypy strict / Ruff / import-linter
  clean, no new ignores.

## Decisions

- **Schema bumped v4 → v5, not "7".** The task said "#7"/"7th version", but the
  `schema_version` is a monotonic counter the loader checks by exact equality; it was at
  v4, so the correct next value is v5. Bumping to 7 would skip v5/v6 and is meaningless.
- **The before/after IS the flip** — the centre reuses `shell_screens.before_after_svg`
  visual language (berry 10/12 → green 0/12) AS the VIOLATED→SATISFIED state-flip, so the
  10→0 reads as the cause (one motion), per the design's core.
- **The centre is derived** (first EVIDENCED HARD_LAW mapping = Art.15), not hardcoded.
- **The disclaimer is on the screen** (`_DISCLAIMER_LEAD` + the EVIDENCE_DISCLAIMER from
  the data) — a locked decision.
- **Visual review via standalone render** — the app embeds `convergence_html` verbatim, so
  the standalone PNG (`docs/assets/m2-0n-convergence-hero.png`) is exactly what the app/shell
  show; headless Chrome can't drive Streamlit's websocket render, so the AppTest proves
  load/replay and the standalone PNG proves the visual.

## Open questions / blockers

- None. Movement 2 is complete; the convergence figure is the paper's contribution figure.

## Next steps (resume here)

Movement 2 is done. The convergence hero is the demo's fourth beat (seam → jurisdiction →
matrix → convergence) and the paper's convergence figure. Future polish (if wanted): a
per-mapping detail panel (the full reason/requirement on demand); a narrated four-hero
walkthrough rehearsal.

## Handoff (fill in on completion)

- **Changed:** demo — `run_result` (v5 + ConvergenceView/ConvergenceMappingView +
  RunResult.convergence), new `demo.convergence`, `runner` wires it, `__init__` exports,
  `recorded_run.json` regenerated. ui — new `convergence_screen` + `convergence_app`,
  `shell_app` hosts it (4th hero, views → ⑦). tests — `test_convergence_screen`,
  `test_convergence_app`, convergence-derivation test in `test_demo_run_result`,
  offline-fallback version bump → v5. docs — MEMORY/TASKS/ROADMAP/feature_list + the hero
  screenshot asset.
- **Verified:** `make verify` green — 410 passed / 2 skipped; lint + mypy strict +
  import-linter clean, no new ignores. Every replay path (seam / jurisdiction / matrix /
  convergence / shell; live + replay) green. Visual review done.
- **Deferred:** none for M2-0n.
- **Recommended next task:** Movement 2 complete — proceed to the paper write-up / the full
  four-hero demo rehearsal, or the next Movement.
