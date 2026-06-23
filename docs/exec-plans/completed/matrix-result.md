# Exec-plan: M1-06 — the characterized-mapping RESULT (matrix block + hero)

- **Slug:** `matrix-result`
- **Feature IDs:** KS-0606 (M1-06) — done. **Movement 1 COMPLETE.**
- **Status:** done
- **Started:** 2026-06-24
- **Owner (session):** agent (Claude)

## Goal & acceptance

Turn the complete seam matrix (P1-P5 in REGISTERED_PAIRS) into a RESULT: a typed
`matrix` block on the RunResult (derived from REGISTERED_PAIRS) + the demo's third hero
screen (a convergence figure), shipped with an AppTest gate. Acceptance = KS-0606
`done_criteria`: the matrix block is derived (add a pair → it appears) at schema v4 with
every replay path migrated and green; the hero renders five attacks → one framework →
results with the axis grouping visual and P4 a DELIBERATE boundary (not an empty slot),
caveats reachable off the hero; AppTest-gated and hosted in the shell.

## Context / constraints

- This re-enters schema+UI territory — the solved bugs apply: components.v1.html (NOT
  st.html), ship the AppTest, no bare-streamlit launch; a schema bump MUST migrate every
  fixture and keep every replay path green (the v2 lesson).
- The matrix must DERIVE from REGISTERED_PAIRS (single source of truth) — nothing hardcoded.
- P4 the boundary is a deliberate proven result, never an empty/missing slot.
- Caveats (P1 rapid-movement overlap; P5 synthetic tool-call channel) = reachable detail,
  OFF the hero.

## Plan

- [x] **Part A (own commit):** RunResult v4 — `matrix` block (`MatrixView`/`MatrixPairView`)
      via `demo.matrix.build_matrix_view` from REGISTERED_PAIRS; migrate `recorded_run.json`
      (regenerate); round-trip + chain re-verify; all replay paths green. Landed first.
- [x] **Part B:** `ui.matrix_screen` (convergence SVG: attacks → framework spine →
      results; axis brackets; P4 dashed boundary; plain-language labels; off-hero caveats
      constant) + `matrix_app`. Visual review via headless-Chrome screenshot.
- [x] **Part C:** AppTest (`test_matrix_app`: live + replay + forced-break) + screen unit
      tests (`test_matrix_screen`: derived-from-data, tokens, boundary-as-result, empty
      state); plug into `shell_app` as the 3rd hero (+ caveats expander); shell AppTest green.
- [x] Verify: `make check && make verify` green; visual review of the running figure.
- [x] Docs: MEMORY, TASKS, ROADMAP, feature_list (KS-0606 done), screenshot asset.

## Progress log

- 2026-06-24 Part A: v4 matrix block derived from REGISTERED_PAIRS; fixture regenerated;
  all replay paths green. Committed separately (landed before the screen).
- 2026-06-24 Part B/C: built the convergence hero; visual review (rotated axis labels,
  fixed the long-typology/CLEAN-tag collision, added column headers); AppTest + screen
  tests; hosted in the shell; caveats as a shell expander.
- 2026-06-24 `make verify` green: 377 passed, 2 skipped, 94.44% coverage; mypy strict /
  Ruff / import-linter clean, no new ignores.

## Decisions

- **The matrix block derives from the SeamPair definitions** (pair.result, pair.crime.typology,
  pair.attack.*), not by running bind() per pair — bind() is gate-tested per pair already;
  the figure reads the declared mapping. Axis derived as `A if owasp_id==LLM01 else B`.
- **Empty financial-substrate is not needed** — the matrix is metadata over the pairs;
  the hero renders from `RunResult.matrix`, with nothing hardcoded (a synthetic extra
  pair appears in the SVG, proven by test).
- **Caveats off the hero, in a shell expander** (`MATRIX_CAVEATS`) — the hero stays clean;
  "is P5 as real as P1?" has an honest, reachable answer.
- **Visual review via standalone render** — the app embeds `matrix_html` verbatim in an
  iframe, so the standalone-rendered PNG (`docs/assets/m1-06-matrix-hero.png`) is exactly
  what the app/shell show; headless Chrome can't drive Streamlit's websocket render, so
  the AppTest proves load/replay and the standalone PNG proves the visual.

## Open questions / blockers

- None. Movement 1 is complete. (The honest caveats are recorded for the paper write-up.)

## Next steps (resume here)

Movement 1 is done. The matrix is the paper's central figure + the demo's "it's a law"
moment. Future Movement 1 polish (if wanted): a richer per-pair detail panel; rehearsal
of the three-hero walkthrough (seam → jurisdiction → matrix).

## Handoff (fill in on completion)

- **Changed:** demo — `run_result` (v4 + MatrixView/MatrixPairView + RunResult.matrix),
  new `demo.matrix`, `runner` wires the matrix, `__init__` exports, `recorded_run.json`
  regenerated. ui — new `matrix_screen` + `matrix_app`, `shell_app` hosts it (3rd hero +
  caveats expander). tests — `test_matrix_screen`, `test_matrix_app`, matrix-derivation
  test in `test_demo_run_result`, offline-fallback version bump (+ feature_list KS-0504
  test-ref rename). docs — MEMORY/TASKS/ROADMAP/feature_list + the hero screenshot asset.
- **Verified:** `make verify` green — 377 passed / 2 skipped / 94.44% cov; lint + mypy
  strict + import-linter clean, no new ignores. Every replay path (seam / jurisdiction /
  shell / matrix; live + replay) green. Visual review done.
- **Deferred:** none for M1-06.
- **Recommended next task:** Movement 1 complete — proceed to the paper write-up / demo
  rehearsal, or the next Movement.
