<!--
Exec-plan (completed). KS-0203 — modality-contrast view-model (deterministic, no UI).
-->

# Exec-plan: Modality-contrast view-model (KS-0203)

- **Slug:** `modality-view-model`
- **Feature IDs:** KS-0203 (Phase 2 / Layer 3). Consumes KS-0202 (crosswalk) and
  KS-0204/0206 (guarded phrasing). Produces the Phase-5 UI's data contract.
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-19
- **Owner (session):** agent
- **Branched from:** `main` @ 9bb2d34 (KS-0206 + KS-0204b merged, verify green).

## Why

Layer 3's headline — EU hard-law conformity vs India self-certification on the
SAME control — needs to be legible structured data before any screen renders it.
KS-0203 ships that as a deterministic, tested view-model. Rendering is Phase 5;
this task stops at the data contract.

## Scope held

- DELIVERABLE = a view-model (structured data), **not a UI**. No Streamlit, HTML,
  styling, or layout. The view SHAPES; it does not recompute the crosswalk or
  re-derive controls — it LOOKS UP what KS-0202 produced.
- Reads `enforcement_modality` and the GUARDED `phrase_summary` (PhrasedSummary).

## What shipped

- `src/keystone/ui/modality_view.py` (edge layer — it calls LLM-edge phrasing, so
  it cannot live in `keystone.core`):
  - `ObligationView` {id, citation, jurisdiction, modality, display_summary, fell_back}
    where `display_summary = PhrasedSummary.text` and `fell_back` is preserved.
  - `ControlView` {control, obligations, modalities, jurisdictions} + properties
    `has_modality_contrast` (BOTH modalities), `modality_mix`
    (HARD_LAW | SELF_CERTIFICATION | BOTH | None), `jurisdiction_mix`.
  - `build_modality_view(crosswalk, *, backend=None)` — pure LOOKUP, order
    inherited from the crosswalk; `backend` is the injectable inference seam.
  - `contrast_controls(views)` — filter over the view-model to the demo highlights.
- `src/keystone/ui/__init__.py` re-exports the view-model WITHOUT importing
  Streamlit (headless-safe).
- `tests/test_modality_view.py` — determinism, modality/jurisdiction summary,
  coverage/no-orphans (mirrors KS-0202 invariants at the view level), guarded
  summary plumbed through, per-obligation `fell_back` preserved, no-mutation
  (both data files byte-identical), empty-control edge case, and a `@milestone`
  test asserting ≥1 contrast control exists in the SHIPPED crosswalk. Phrasing is
  faked (fake backend, no NIM/credits), same pattern as KS-0204's fast tests.

## Decisions

- **Placement = `keystone.ui`** (the "Phase-5 UI's data contract"): outermost edge
  layer, may depend on core + the LLM seam, nothing depends on it. Keeps the
  import-linter core→edge contract green. Not `keystone.core` (calls phrasing).
- **`backend` injection** (not a `phrase` callable) to reuse KS-0204's exact
  fake-backend seam in the fast gate.
- View types are **frozen dataclasses** (data already validated by the core
  Pydantic models); `modality_mix`/`jurisdiction_mix`/`has_modality_contrast` are
  derived **properties** so there's one source of truth.
- No new ADR (implements existing ADR-0008 boundary + ADR-0012 §4 fidelity).

## Verification

- `make check` green; `make verify` exit 0 — 138 passed / 2 skipped, total
  coverage 95.7% (`modality_view.py` 100%).
- import-linter "core must not import the edge" KEPT (1 kept, 0 broken).
- `obligations.json` AND `controls.json` byte-identical after building the view
  (no write-back); asserted by test + `git diff` clean on data files.

## The contrast lands on 2 controls (demo money-shots)

- **CTL-GOV-01** (Governance, leadership & accountability): HARD_LAW = DORA Art. 5
  (EU) + DPDPA s.8/s.10 (India); SELF_CERTIFICATION = RBI sutras "Trust is the
  Foundation" (OBL-RBI-001) + "Accountability" (OBL-RBI-002). Jurisdictions: BOTH.
- **CTL-TRANSP-01** (Transparency & explainability): HARD_LAW = EU AI Act Art. 13
  (OBL-EUAI-013); SELF_CERTIFICATION = RBI sutra "Understandable by Design"
  (OBL-RBI-003). Jurisdictions: BOTH.

## Next

Phase 2 (Layer 3) feature set complete. Next → Phase 3 / Layer 2 (AI Assurance
Loop, KS-03xx). Phase 5 will render this view-model. See [[MEMORY.md]].
