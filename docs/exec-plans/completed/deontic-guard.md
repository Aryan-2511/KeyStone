<!--
Exec-plan (completed). KS-0206 — deterministic deontic-strength guard for phrasing.
-->

# Exec-plan: Deterministic deontic-strength guard (KS-0206)

- **Slug:** `deontic-guard`
- **Feature IDs:** KS-0206 (Phase 2 / Layer 3). Hardens KS-0204; must precede
  KS-0203 (the modality-contrast screen renders phrased text next to labels).
- **Status:** done (archived 2026-06-18)
- **Started:** 2026-06-18
- **Owner (session):** agent
- **Branched from:** `main` @ d44a5d5 (KS-0204 merged).

## Why

KS-0204 review found the 9B no-think model occasionally shifts modal force when
rewording — both directions: it hardened an RBI advisory body ("should/with" →
"must") and, when the prompt was tightened, softened an EU AI Act "shall" →
"should". Modal force (binding vs advisory) is a FACT, already encoded by
`enforcement_modality`; it must not be left to probabilistic phrasing. Prompt
steering is unreliable on this model, so the fix is deterministic.

## What shipped

- `keystone/core/deontic.py` (deterministic core, no LLM): `modal_profile(text)
  -> ModalProfile(binding, advisory)` over precise lexicons (BINDING =
  must/shall/mandatory/"required to"/oblig*, negation-aware so "not binding"/"not
  mandatory" don't count; ambiguous noun "requirement" excluded), and
  `drifts(source, candidate)` → True on strengthening (`cand.binding>0 &
  src.binding==0`) or weakening (`src.binding>0 & cand.binding==0 &
  cand.advisory>0`).
- `keystone/llm/phrasing.py`: `phrase_summary` now returns
  `PhrasedSummary(text, fell_back)`. On `drifts(summary, phrased)` it returns the
  curated `summary` verbatim (`fell_back=True`) — certainly-faithful over
  probably-faithful. Compares to the SOURCE (not `enforcement_modality` alone) so
  curated advisory text that legitimately contains "must" (RBI-001) isn't a false
  positive.
- Tests: `tests/test_deontic.py` (classifier + drift truth table, incl. the live
  cases) and guard tests in `tests/test_phrasing.py` (faithful → pass; strengthen
  / weaken → fall back). feature_list KS-0206 done; ROADMAP/TASKS/MEMORY updated.

## Decisions

- Classifier in **core** ("facts belong to core"); guard wraps phrasing in the
  **edge** (user-confirmed). `PhrasedSummary` result object so the UI can label
  fallbacks (user-confirmed). No new ADR (implements ADR-0012 §4 fidelity).
- BINDING lexicon favours precision → the guard errs toward fallback (safe).
- Added as a feature_list item KS-0206 (phase-2 extension); flagged for review —
  can be folded into KS-0204 if preferred.

## Verification

- `make verify`: exit 0, 108 passed / 2 skipped, coverage 94.8% (`phrasing.py`
  100%). import-linter core→edge KEPT; `obligations.json` byte-identical.
- Live end-to-end: RBI-001/RBI-002 (SELF_CERTIFICATION) drift → `fell_back=True`
  (curated summary shown); EUAI-012/PMLA-008 (HARD_LAW) faithful → reword shown.

## Hardening — 2026-06-18 (completes the KS-0206 spec; branch `ks-0204b-deontic-guard`)

The first cut was binary + modality-blind. Per the full spec it was hardened
(KS-0206 id KEPT — no rename; the work completes the original spec):

- **Tiered classifier** `classify(text) -> Tier` (STRONG/MEDIUM/WEAK/UNCLASSIFIED),
  replacing the binary `modal_profile`. Negation-awareness preserved.
- **`detect_modal_drift(source, phrased, enforcement_modality)`** replaces
  `drifts()` — **removed, no shim**, single caller (`phrase_summary`) updated.
- **Uncertain-on-strong → fallback** via the STRONG XOR (a STRONG source reworded
  with no modal verb now falls back). The both-UNCLASSIFIED pass-through is
  XOR-guarded so it can't re-open that hole for a STRONG source.
- **HARD_LAW cross-check**: a hard-law node phrased advisory falls back.
- **Chosen scope line (explicit decision, MEMORY.md):** only STRONG transitions +
  HARD_LAW are hard-protected; within-advisory (should↔may) drift off hard-law is
  accepted latitude — a deliberate line, not a gap.
- **Fallback-not-fail** unchanged (req 4): `PhrasedSummary(text, fell_back)`.
- **28-node fallback rate measured: 2/28 (~7%)** — far under the >½ stop.
- `make verify` exit 0 (123 fast + slow-skips), import-linter core→edge KEPT,
  `obligations.json` byte-identical.

## Next

KS-0203 (modality contrast) — now safe: it renders `PhrasedSummary.text`, which
never drifts vs the binding/advisory label. See [[MEMORY.md]].
