<!--
Exec-plan. Keep it current AS YOU WORK — it is the handoff that lets any future
session resume cleanly. On completion run the verify gate and move to
docs/exec-plans/completed/ (the /finish-task command does this).
-->

# Exec-plan: Curated obligation graph with per-node source citations

- **Slug:** `obligation-graph`
- **Feature IDs:** KS-0201 (this plan). Phase 2 / Layer 3 — Obligation Mapper.
  Sibling items in the same layer, NOT in scope here: KS-0202 (crosswalk/dedup),
  KS-0203 (modality contrast), KS-0204 (LLM-edge summaries), KS-0205
  (citation-validation gate).
- **Status:** active
- **Started:** 2026-06-16
- **Owner (session):** agent

## Goal & acceptance

Build a **deterministic, curated obligation graph** of ~25–30 nodes spanning
EU AI Act Art. 9–15, DORA, India DPDP Act + DPDP Rules 2025, RBI responsible-AI
guidance, and PMLA/FIU-IND, where **every node carries a non-empty source
citation** (instrument + article/section).

- **`done_criteria` (KS-0201, feature_list.json):** "the graph has 25–30 nodes
  covering EU AI Act Art. 9–15, DORA, India DPDP Act + DPDP Rules 2025, RBI
  responsible-AI, and PMLA/FIU-IND, and every node carries a non-empty source
  citation (instrument + article/section)."
- **QUALITY.md rows that bind this work:** #1 tests pass · #3 scope valid
  (`done_criteria` met, `tests` exist + pass) · #4 mypy strict · #5 ruff/`S` ·
  #6 architecture (this is deterministic core — must NOT import the LLM edge) ·
  #7 docs fresh (ADR if a structural choice is made; this plan kept current) ·
  #8 synthetic data only.
- **Scope guard:** the LLM-edge phrasing (KS-0204) and the build-failing
  citation-validation gate (KS-0205) are *separate* features. This task delivers
  the data + its loader/model + behavioral tests; the strict accuracy-budget
  gate lands in KS-0205. Keep that boundary clean (note any overlap in Decisions).

## Context / constraints

- `CLAUDE.md` non-negotiables: Python 3.12 only, `uv` only, strict gates never
  weakened, **synthetic data only / no secrets**. Mechanical enforcement > prose.
- **Layer boundary (ADR-0008):** obligation graph is deterministic — place under
  `keystone.core.*` (e.g. `keystone.core.obligations`). import-linter forbids
  `keystone.core` from importing `agents/policy/llm/ui/assurance`. Citations and
  graph logic stay LLM-free (the LLM only phrases summaries, KS-0204).
- **Roadmap alignment (ADR-0011):** Phase 2 = Layer 3 Obligation Mapper; this is
  the first real product layer. See `ROADMAP.md`, `docs/feature_list.json`.
- **Citations are legal references**, not freeform: model an explicit citation
  field (instrument + article/section) so KS-0205 can validate it mechanically.
  These are public legal instruments, not "real data" in the synthetic-only
  sense — but cite accurately; an unsourced/wrong article is a defect.
- Patterns to mirror: `keystone.core.ledger` (deterministic core module + model
  + adversarial tests) and `tests/test_ledger.py`.

## Plan

- [ ] Audit: read `keystone.core.ledger` + its tests for the core-module idiom;
      confirm where the graph fits (`keystone.core.obligations`) and the
      import-linter contract already covers it.
- [ ] Model: define an `Obligation` node (id, instrument, article/section
      citation, regime/jurisdiction, modality hook for KS-0203, summary slot for
      KS-0204) + edges/relations. Decide storage (in-repo data file vs. code).
- [ ] Curate ~25–30 nodes across the five instruments, each with a verified
      citation. Record the source list so citations are auditable.
- [ ] Loader + deterministic accessors (no LLM, no network). Pure, typed.
- [ ] Tests: node count in [25,30]; all five instruments present; every node has
      a non-empty, well-formed citation (behavioral assertion now — the
      build-failing gate is KS-0205); loader determinism.
- [ ] Wire the test refs into `feature_list.json` KS-0201; flip status → done.
- [ ] Verify: `make verify` green.
- [ ] Update human views (TASKS.md) + this plan's Handoff; ADR if a structural
      choice was made (e.g. data-file format, citation schema).

## Progress log

- 2026-06-16 created plan. Roadmap realigned (ADR-0011, commit 1ac496e) so
  Phase 2 = Obligation Mapper and KS-0201 = this graph. No code yet.
- 2026-06-16 data model + storage decisions locked in ADR-0012 (storage=JSON data
  file + fail-loud Pydantic model; structured citation; control library Option A
  with conditions 5a/5b). Still no model/loader/data/curation.

## Decisions

- **Obligation data model + storage locked — see ADR-0012.** Storage = a JSON
  data file under `keystone.core.obligations/data/` loaded via a fail-loud
  Pydantic v2 model; structured `Citation` object (instrument/provision/title/
  url?/retrieved?); enums `Instrument`/`Modality`/`Jurisdiction`. Control library
  = **Option A** (own data file; obligations reference by `control_id`), with
  `control_ids` optional/empty in KS-0201 (5a) and KS-0202 owning a fail-loud
  referential-integrity validator (5b). LLM phrasing (KS-0204) is edge-side and
  must not write back into this core data.

## Open questions / blockers

- None blocking. KS-0201's `done_criteria` is well-specified. The citation
  *schema* is shared with KS-0205 (the gate) — design it here so KS-0205 can
  enforce it without reshaping the data.

## Next steps (resume here)

Start with the audit step: read `src/keystone/core/ledger.py` + `tests/test_ledger.py`
for the deterministic-core idiom, then draft the `Obligation` model under
`keystone.core.obligations`. Curate citations against primary sources; do not
guess article numbers.

## Handoff (fill in on completion)

- _TBD_ — what changed, `make verify` result pasted, what was deferred (KS-0202–0205),
  recommended next task (likely KS-0205 citation-validation gate, then KS-0202).
