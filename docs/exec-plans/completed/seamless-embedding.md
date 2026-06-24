# Exec-plan: UI-01 — seamless embedding (kill the "pasted picture" seam)

- **Slug:** `seamless-embedding`
- **Feature IDs:** KS-0610 (UI-01) — done; unblocks UI-02 (the live-execution view)
- **Status:** done
- **Started:** 2026-06-25
- **Owner (session):** agent (Claude)

## Goal & acceptance

Make all four heroes sit FLUSH on the Streamlit page — ONE shared background token across
the theme + every SVG fill + every iframe wrapper, iframe chrome stripped. Systemic
(single source), not four one-off patches. Cosmetic + additive: no logic/schema/data
change. Acceptance = KS-0610 `done_criteria`: one token drives all three surfaces
(drift-guarded); the fix is systemic; purely cosmetic with all replay paths green.

## Step-1 theme audit (findings)

- (a) `.streamlit/config.toml` HAS a `[theme]` with `backgroundColor = #1A1A1A` (`T.BG`),
  `secondaryBackgroundColor = #14171C` (`PANEL`). Mirrors `tokens.streamlit_theme()`.
- (b) Every hero SVG fills with `T.INK` (#0E0F12) via the shared `svg.document` — PLUS a
  1px outer hairline border (the framed-rectangle edge). All four heroes use `document`.
- (c) Each `*_html` wrapper sets `html,body{margin:0;background:T.INK}`; embedded via
  `components.html(..., height=…, scrolling=False)`.
- (d) `tokens` had THREE near-blacks: INK (canvas), PANEL (sidebar), BG (page). The theme
  used BG, the SVG/iframe used INK — **NOT a single source; they disagreed (the seam)**.
  Root cause: page bg (BG #1A1A1A) ≠ canvas bg (INK #0E0F12), + the SVG outer border.

## Plan

- [x] Make `T.INK` the single app background; `streamlit_theme().backgroundColor` → INK.
- [x] Mirror in `.streamlit/config.toml` (`backgroundColor = #0E0F12`).
- [x] Drop the outer hairline border from `svg.document` (the framed-rectangle edge).
- [x] New `keystone.ui.embed.embed_hero` — one embed path (SEAMLESS_CSS iframe reset +
      `components.html`), keeping KS-0501 sizing; route all four hero apps + the shell.
- [x] Extend `test_ui_tokens` to assert theme == SVG canvas == iframe surface == INK.
- [x] Verify + visual review (before/after screenshots).
- [x] Docs: MEMORY / TASKS / feature_list (KS-0610 done) + the before/after assets.

## Progress log

- 2026-06-25 audit: page BG ≠ SVG INK; + SVG outer border. Reconciled all three to INK.
- 2026-06-25 before/after render confirms the seam is gone (flush, no rectangle/border).
- 2026-06-25 `make verify` green: 411 passed, 2 skipped; mypy strict / Ruff / import-linter
  clean, no new ignores. All four AppTests + replay paths + recorded fallback green.

## Decisions

- **Unified on INK (the deep canvas), not BG** — the heroes were designed/reviewed on INK;
  making the PAGE match INK preserves the hero look exactly and just darkens the page (vs
  lightening every hero). `T.BG` is now legacy (palette only).
- **Removed the SVG outer border** (in the shared `document`) — with page == canvas, the 1px
  frame was the only remaining "pasted picture" edge. Internal panel hairlines stay (content).
- **One `embed_hero`** so the iframe-chrome strip is single-source; kept `components.v1.html`
  + height-from-viewBox (did NOT regress to st.html — the KS-0501 bug).

## Open questions / blockers

- None. "Seamless" is a looks judgment a test can't make — the before/after assets show it,
  and the human eyeballs it live before merge (live Streamlit screenshots show only the
  loading skeleton in headless Chrome — the M1-06 finding).

## Next steps (resume here)

UI-02 — the live-execution view.

## Handoff (fill in on completion)

- **Changed:** `tokens` (INK = the single app bg; streamlit_theme → INK), `.streamlit/config.toml`
  (mirror), `svg.document` (drop outer border), new `keystone.ui.embed`, the four hero apps +
  shell route through `embed_hero` (components import removed); `test_ui_tokens` reconciliation
  test; docs + before/after assets (`docs/assets/ui-01-before-seam.png`, `ui-01-after-seamless.png`).
- **Verified:** `make verify` green — 411 passed / 2 skipped; lint + mypy strict + import-linter
  clean, no new ignores. **No logic/data/schema change.**
- **Deferred:** none.
- **Recommended next task:** UI-02 (the live-execution view).
