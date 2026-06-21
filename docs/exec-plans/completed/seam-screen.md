<!--
Exec-plan (completed). KS-0501 — shared design system + the seam hero screen.
The single most important screen in the project: the thesis as an image.
-->

# Exec-plan: design system + the seam hero screen (KS-0501)

- **Slug:** `seam-screen`
- **Feature IDs:** KS-0501 (Phase 5 / Integration & demo). `depends_on` KS-0500
  (the run-result contract it renders from).
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-21
- **Owner (session):** agent
- **Branched from:** `main` @ 1ff2c09 (KS-0500 merged).

## Why

The climax visual: make "ONE event, TWO failures" instant and undeniable — the same
transaction shown simultaneously as an AI-security vulnerability (Layer 2) and a
financial crime (Layer 1), bound on one signature. It must read from the real
KS-0500 run-result (the "it's real" claim), and it establishes the shared design
system the other Phase-5 screens (KS-0502/0503) inherit.

## What shipped

- `keystone/ui/tokens.py` — the ONE design system: palette (the deck's — NVIDIA
  green anchor; teal/purple/berry/amber layer semantics; near-dark evidence ramp),
  a deliberate type trio (Space Grotesk / Inter / IBM Plex Mono — NOT Streamlit
  defaults), spacing, `LAYER_COLOR`, `streamlit_theme()`, `fonts_css()`.
- `.streamlit/config.toml` — the Streamlit theme, mirroring `tokens.streamlit_theme()`.
- `keystone/ui/seam_screen.py` — the hero as a custom, self-contained SVG built from
  a `RunResult`: the seam transaction as an amber "target" (crosshair corners) at
  centre, the L2 (purple) + L1 (berry) findings flanking, and the signature element
  — an amber CONVERGENCE where two coloured connectors + the tx spine drop into a
  binding bar reading `[tx id] ≡ [signature]` with the plain-language thesis. Plain-
  language translations on each finding (the clarity rule). Pure string-building (no
  Streamlit import) so it exports standalone for the screenshot. `MISSING` (▮) +
  empty state for honest degradation.
- `keystone/ui/seam_app.py` — `streamlit run src/keystone/ui/seam_app.py`: live
  (`build_run_result`) or replay (`load_run_result`, default = the committed
  fixture); honest error + empty state if a saved run can't load. Embeds the hero via
  `st.components.v1.html` (an iframe) at `SEAM_HEIGHT_PX`.
- `tests/fixtures/seam_run_result.json` — a committed run for replay + tests.
- `tests/test_ui_tokens.py`, `tests/test_seam_screen.py`.
- Review artifacts: `docs/assets/ks-0501-seam-screen.png` (the hero design) and
  `docs/assets/ks-0501-seam-app.png` (the RUNNING app — replay mode).

![The seam hero](../../assets/ks-0501-seam-screen.png)
![The seam hero in the running app](../../assets/ks-0501-seam-app.png)

## Two app-breaking bugs found in review (both fixed) — and the gate hole closed

1. **Blank panel (`st.html`).** First cut embedded the SVG with `st.html`, which
   SANITISES inline SVG away — the hero showed as a BLANK main panel while every gate
   was green. Fix: embed via `st.components.v1.html` (an iframe) at a derived
   `SEAM_HEIGHT_PX` (from the viewBox, so it never clips).
2. **`ImportError` on load.** The app imported `SEAM_HEIGHT_PX`; a stale checkout
   could miss the export, crashing `seam_app.py` on import — again with green gates.

**Root cause of both slipping through: the gate never RAN the app.** No test imported
`seam_app.py` (it sat at 0% coverage), so an import/render error there could not fail
`make verify`. Fixed by `tests/test_seam_app.py`, which runs the real Streamlit script
via `streamlit.testing.v1.AppTest` (live AND replay) and asserts no exception — this
reproduces the exact `ImportError` when the export is removed (verified by temporarily
breaking it), so a broken demo app now fails the build.

Re-verified by actually running `streamlit run src/keystone/ui/seam_app.py` and
watching the hero draw in the main panel — live and replay
(`docs/assets/ks-0501-seam-app.png`). Lessons in MEMORY.md: custom SVG →
`components.v1.html`, never `st.html`; and a Streamlit screen needs an `AppTest`
(or running-app) gate, not just helper-level unit tests.

## Decisions

- **One token source, mechanically enforced.** `tokens.py` is authoritative;
  `config.toml` mirrors it and `test_ui_tokens.py` fails on drift — the fix for the
  cross-screen consistency concern (shared tokens, not one render method).
- **Custom SVG, not Streamlit widgets, for the hero.** Pixel-precise composition and
  the convergence connectors need it; embedded via `st.html`. Boldness spent in ONE
  place (the amber binding/convergence); everything else quiet (evidence aesthetic,
  mono ids, hairlines) — no metric-card/gradient dashboard look.
- **Static (locked).** No animation this build; the drama is the composition.
- **Reads ONLY the run-result.** Every value (tx id, amount, accounts, memo, both
  findings, OWASP class, signature, arc/chain) comes from `keystone.demo` — verified
  by a sentinel-substitution test; no hero value is hardcoded or mocked.
- **PLR0913 fixed, not ignored.** Bundled text styling into a `TextStyle` NamedTuple
  rather than relax the lint (gates never weakened).

## Verification

- `make check` green OFFLINE — `tokens.py` 100%, `seam_screen.py` 97%, total 90%;
  268 passed.
- `make verify` exit 0 — full suite; import-linter KEPT; feature_list valid.
- **Visual QA** (the real review): iterated on the rendered image — strengthened the
  convergence into the focal point, added the plain thesis line, fixed a footer
  overflow. Then verified the RUNNING Streamlit app (live + replay) via the DevTools
  Protocol, which is what surfaced the `st.html` blank-panel bug above. Final in-app
  capture committed: "one transaction, two failures" reads instantly, the binding is
  the focal point, and it reads as designed (not default-Streamlit).

## Next

KS-0502 — the jurisdiction-contrast hero (EU vs India) — inherits this design system
and renders the same finding's regulatory mapping from the run-result.
