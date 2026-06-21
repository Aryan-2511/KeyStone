<!--
Exec-plan (completed). KS-0404 — regulator-format report generation (fact/language split).
-->

# Exec-plan: Report generation (KS-0404)

- **Slug:** `report-generation`
- **Feature IDs:** KS-0404 (Phase 4 / Layer 1 extension). `depends_on` KS-0402
  (builds a report from a FATF finding).
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-21
- **Owner (session):** agent
- **Branched from:** `main` @ ee5b684 (KS-0403 merged).

## Why

Turn a detected fraud finding into a regulator-format report. The discipline: the
deterministic core decides WHAT goes in (facts); the guarded LLM edge phrases only
the SAR/STR NARRATIVE — facts must never be invented by the LLM.

## What shipped

- `keystone/core/reporting/facts.py` (CORE) — `ReportFacts` (system of record),
  `assemble_facts(finding, transactions)`, `template_narrative` (always-faithful
  floor), `narrative_is_faithful` (deterministic guard: every number/id/typology in
  the narrative must be in the facts; strips ids before the number check to avoid
  over-fallback).
- `keystone/core/reporting/report.py` (CORE) — `Report` (DRAFT/SIGNED), `sign_off`,
  the format-agnostic adapters `to_finnet` (FINnet 2.0 STR, primary) / `to_goaml`
  (UN goAML, second) + `render`, and `record_report` → ledger (`report-generator`,
  L1, `report_drafted`/`report_signed`).
- `keystone/llm/report_narrative.py` (EDGE) — `generate_narrative(facts, backend)`
  (calls the inference seam, applies the guard, falls back to the template) and
  `draft_report(finding, transactions, backend)`.
- `tests/test_reporting.py` — facts exactness, both adapters over the same facts,
  the guard fall-back on invented number/id/typology, the over-fallback guard (real
  ids kept), sign-off + ledger, no-mutation, and a slow live narrative that is
  always faithful (or falls back).

## Decisions

- **Fact/language split mirrors obligations(core)/phrasing(edge).** Facts + guard +
  adapters are CORE (no LLM); only narrative generation is edge. import-linter KEPT.
- **Fall-back-not-fail** (deontic-guard discipline): a filing is never emitted with a
  hallucinated figure; human sign-off does NOT replace the deterministic check.
- **Number check strips ACC-/TXN- ids first** so a narrative citing a real id is not
  read as an invented amount (avoids over-fallback — the live model's faithful prose
  is kept; it falls back only on genuine deviation).
- **Adapters model KNOWN STR/goAML fields with marked `<PLACEHOLDER>` values** — no
  fabricated official schema (surfaced rather than invented authority).

## Verification

- `make check` green — reporting core 100% / report.py 95%, edge 100%, total 91.4%.
- `make verify` exit 0 — 249 passed / 2 skipped; import-linter core→edge KEPT; core
  data byte-identical (no write-back).
- Sample: a STRUCTURING finding on ACC-0004 → FINnet STR with 9 suspicious
  transactions + the SAME 9 in goAML; faithful narrative kept; an invented-fact
  narrative falls back to the faithful template. Live 3B narrative is faithful most
  runs (kept) and falls back on temperature variance — never unfaithful.

## Next

KS-0405 — the Layer-1 milestone (ingest → FATF finding → drafted/signed report →
verifiable ledger chain). Then Phase 5 (integration & demo).
