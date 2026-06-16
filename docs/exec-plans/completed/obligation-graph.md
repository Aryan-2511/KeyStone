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
- **Status:** done (archived 2026-06-17)
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

- [x] Audit: read `keystone.core.ledger` + its tests for the core-module idiom;
      confirm where the graph fits (`keystone.core.obligations`) and the
      import-linter contract already covers it.
- [x] Model: define an `Obligation` node (id, instrument, article/section
      citation, regime/jurisdiction, modality hook for KS-0203, summary slot for
      KS-0204). Storage = packaged JSON data file (per ADR-0012).
- [x] Curate 28 nodes across all six instruments, each with a verified
      citation (EU AI Act Art. 9–15; DORA Art. 5/6/17/19/24/28; DPDP Act
      ss. 5/6/8/9/10/11; DPDP Rules 2025 r. 4/6/7; RBI FREE-AI sutras 1/5/6;
      PMLA s. 12 + PML Rules 2005 r. 8/9).
- [x] Loader + deterministic accessors (no LLM, no network). Pure, typed.
- [x] Tests: node count in [25,30]; all instruments present; EU AI Act covers
      Art. 9–15; every node has a non-empty, well-formed citation (behavioral
      assertion now — the build-failing gate is KS-0205); loader determinism +
      fail-loud paths; model cross-field invariants.
- [x] Wire the test refs into `feature_list.json` KS-0201; flip status → done.
- [~] Verify: `make verify` — KS-0201's own gates all green (52 passed,
      1 skipped; mypy strict; ruff incl. `S`; import-linter architecture;
      coverage 90%). Gate's ONLY red is a PRE-EXISTING transitive CVE — see
      Blockers.
- [x] Update human views (TASKS.md) + this plan's Handoff. No new ADR: model +
      storage were already locked in ADR-0012 and curation followed it exactly.

## Progress log

- 2026-06-16 created plan. Roadmap realigned (ADR-0011, commit 1ac496e) so
  Phase 2 = Obligation Mapper and KS-0201 = this graph. No code yet.
- 2026-06-16 data model + storage decisions locked in ADR-0012 (storage=JSON data
  file + fail-loud Pydantic model; structured citation; control library Option A
  with conditions 5a/5b). Still no model/loader/data/curation.
- 2026-06-17 implemented: `models.py` (already drafted), `loader.py` (already
  drafted), added `__init__.py` (public surface), curated `data/obligations.json`
  (28 nodes), `tests/test_obligations.py` (23 tests), wired KS-0201 → done in
  `feature_list.json`, ticked TASKS.md. All KS-0201 gates green; the only
  `make verify` failure is a pre-existing transitive `cryptography` CVE.

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

- **Pre-existing `pip-audit` failure blocks a fully-green `make verify` —
  NOT introduced by KS-0201 and not fixable from within this task.** `pip-audit`
  flags `cryptography` 46.0.7 (GHSA-537c-gmf6-5ccf, fixed in 48.0.1). It is a
  transitive dep; `nvidia-nat-core==1.7.0` pins `cryptography>=46.0.6,<47`, so
  the fixed version is excluded unless the NVIDIA stack is bumped or an override
  is added. I touched no dependencies (`git diff uv.lock` is empty), so this CVE
  is present on `main` independently of this work. **Needs a decision** (bump
  `nvidia-nat`, add a `[tool.uv]` override, or a documented `pip-audit --ignore`
  — the last weakens a gate, so per CLAUDE.md do not do it without sign-off).
  Recommend handling as a separate dependency-hygiene task.
- Citation accuracy caveat for KS-0205: the RBI nodes cite the FREE-AI
  framework's "sutras" (guiding principles) rather than numbered statutory
  sections, and the DPDP Rules 2025 rule numbers should be re-verified against
  the notified text when KS-0205's accuracy gate lands. `url`/`retrieved` are
  populated only for the EU instruments (EUR-Lex ELI links); Indian instruments
  have `url`/`retrieved` null on purpose (not live-verified) — KS-0205 can
  surface that as staleness.

## Next steps (resume here)

KS-0201 is complete. Recommended next task: **KS-0205** (citation-validation
accuracy budget) — it reduces to schema-validating `data/obligations.json`
against per-instrument `provision` patterns and flagging missing/stale
`retrieved` dates, building directly on the locked schema. Then **KS-0202**
(control library + the 5b referential-integrity validator over `control_ids`).

## Handoff

- **What changed:** added `src/keystone/core/obligations/__init__.py` (public
  surface), `data/obligations.json` (28 curated nodes spanning all six
  instruments), and `tests/test_obligations.py` (23 tests). `models.py` and
  `loader.py` were already drafted from the prior session and match ADR-0012
  unchanged. Wired KS-0201 → `done` with 7 test refs in `feature_list.json`;
  ticked the TASKS.md row.
- **`make verify` result:** all KS-0201-relevant gates green — `52 passed,
  1 skipped`, mypy strict clean, ruff (incl. `S`) clean, import-linter
  architecture boundary holds (obligations is deterministic core, no edge
  imports), coverage 90% (obligations module 100%). The gate exits non-zero
  ONLY on the pre-existing `cryptography` CVE described under Blockers.
- **Deferred:** KS-0202 (control library + integrity check), KS-0203 (modality
  contrast — `enforcement_modality` is populated and both values appear),
  KS-0204 (LLM-edge summary phrasing), KS-0205 (citation-validation gate).
- **Archived 2026-06-17** at the user's direction: KS-0201 itself is complete
  and all its gates pass. The remaining `make verify` red (transitive
  `cryptography` CVE) was split off into a separate dependency-hygiene task
  (see `docs/exec-plans/active/dependency-hygiene-cryptography.md`).
