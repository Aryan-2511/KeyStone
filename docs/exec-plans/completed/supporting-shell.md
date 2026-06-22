<!--
Exec-plan (completed). KS-0503 — supporting shell (the frame around the two heroes).
Also: the v2-replay regression fix that preceded it (version-aware loader), and the
RunResult v3 referenced-assurance addition.
-->

# Exec-plan: supporting shell (KS-0503)

- **Slug:** `supporting-shell`
- **Feature IDs:** KS-0503 (Phase 5 / Integration & demo). `depends_on` KS-0500/0501/0502.
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-22
- **Owner (session):** agent
- **Branched from:** `main` @ 950d1cf (KS-0502 + the v2-replay fix merged).

## Why

The two heroes carry the thesis; the shell is the navigable frame that holds them
plus the supporting evidence — the hash-chained ledger, the cross-layer posture, and
the assurance before/after. Minimal-but-present: a polished frame, not a dashboard.

## What shipped

- **RunResult schema v3** (the agreed scoped addition): `ai_security.assurance`
  (`AssuranceView`) carries the referenced Layer-2 before/after from the single-source
  `keystone.assurance.REFERENCED_ASSURANCE` constant (10/12 → 0/12, exploit before→after).
  The KS-0302/0304 loop tests now assert their real output EQUALS the constant (so it
  can't drift); fixture regenerated; new demo test.
- **`keystone/ui/shell_screens.py`** — the three supporting views on `keystone.ui.svg`:
  `ledger_svg` (the arc + chain + real entry-hash prefixes), `posture_svg` (L3/L2/L1 at
  a glance), `before_after_svg` (10/12 → 0/12, found→patched). Quiet, plain-language,
  ▮ / empty states.
- **`keystone/ui/shell_app.py`** — the sidebar shell: a View nav across all five views
  + the live/replay Data source. HOSTS the heroes verbatim (`seam_html` /
  `jurisdiction_html`), embeds via `st.components.v1.html`.
- **Tests:** `tests/test_shell_screens.py` (real data, tokens-only colour, data-driven
  not hardcoded, empty state) + `tests/test_shell_app.py` (AppTest cycles ALL views,
  live + replay).
- Review artifacts (from the RUNNING shell): `docs/assets/ks-0503-shell-seam.png`,
  `ks-0503-ledger.png`, `ks-0503-posture.png`, `ks-0503-before-after.png`.

![Shell hosting the seam hero](../../assets/ks-0503-shell-seam.png)
![Evidence ledger view](../../assets/ks-0503-ledger.png)
![Cross-layer posture view](../../assets/ks-0503-posture.png)
![Assurance before/after view](../../assets/ks-0503-before-after.png)

## Decisions

- **Host, don't reimplement.** The shell imports `seam_html` / `jurisdiction_html` and
  renders them; zero hero logic duplicated.
- **RunResult v3 (assurance counts only).** Surfaced the data gap (STOP condition);
  per the decision, added the referenced before/after only and kept L3 posture
  qualitative from the EU/India data already in v2 (don't gold-plate). Referenced via a
  single constant the loop tests assert against — real, no re-run, no drift.
- **AppTest radios by label, not index.** The shell creates two radios (View, Data
  source); selecting by `.label` is robust to creation order (an index assumption bit
  the first cut — caught by the gate).
- **Quiet frame.** No new boldness; the supporting views inherit the evidence
  aesthetic so the whole app is one product.

## Verification

- `make check` + `make verify` green (294 passed); mypy strict, Ruff (PL/SIM resolved
  without ignores), import-linter KEPT.
- **AppTest gate** demonstrated to fail on a forced break (`module 'shell_screens' has
  no attribute 'LEDGER_HEIGHT_PX'` at `shell_app.py:42`), then restored.
- **Visual QA** — ran `uv run streamlit run src/keystone/ui/shell_app.py` and captured
  the RUNNING shell via the DevTools Protocol: both heroes hosted (seam live,
  jurisdiction replay) and all three supporting views (ledger live, posture + before/
  after replay). Nav works; the shell reads as one product with the heroes.

## Next

KS-0504 — recorded-run fallback (offline replay default), then KS-0505 — demo script +
rehearsal. The version-aware loader + the committed v2/v3 fixture already give the
offline replay foundation KS-0504 packages.
