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
  fixture); honest error + empty state if a saved run can't load.
- `tests/fixtures/seam_run_result.json` — a committed run for replay + tests.
- `tests/test_ui_tokens.py`, `tests/test_seam_screen.py`.
- The review artifact: `docs/assets/ks-0501-seam-screen.png`.

![The seam hero](../../assets/ks-0501-seam-screen.png)

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
- **Visual QA** (the real review): rendered the SVG over the saved run in headless
  Chrome and iterated on the image — strengthened the convergence into the focal
  point, added the plain thesis line, fixed a footer overflow. Final screenshot
  committed (above): "one transaction, two failures" reads instantly, the binding is
  the clear focal point, and it reads as designed (not default-Streamlit).

## Next

KS-0502 — the jurisdiction-contrast hero (EU vs India) — inherits this design system
and renders the same finding's regulatory mapping from the run-result.
