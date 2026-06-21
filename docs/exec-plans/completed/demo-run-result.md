<!--
Exec-plan (completed). KS-0500 — demo runner + serializable run-result (the UI's typed contract).
Enabling dependency for the Phase-5 narrative-first screens (KS-0501 seam hero etc.).
-->

# Exec-plan: demo runner + serializable run-result (KS-0500)

- **Slug:** `demo-run-result`
- **Feature IDs:** KS-0500 (Phase 5 / Integration & demo). `depends_on` KS-0405
  (the Layer-1 milestone arc it composes).
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-21
- **Owner (session):** agent
- **Branched from:** `main` @ f5d87c8 (KS-0405 merged).

## Why

KS-0501 (the seam hero screen) and the rest of Phase 5 must render from a real,
typed run-result — the "it's real" claim forbids mocked data. No such object
existed: the original task assumed a "KS-0500 run-result" that was neither in main
nor the roadmap. Per the user's call, Phase 5 was realigned narrative-first
(KS-0500 = runner + run-result; 0501 = design system + seam hero; 0502 =
jurisdiction hero; 0503 = supporting shell; 0504 = recorded-run fallback; 0505 =
script + rehearsal), and KS-0500 is built first so KS-0501 lands on a main that has
the contract.

## What shipped

- `keystone/demo/run_result.py` — the typed, frozen, JSON-serializable `RunResult`
  and its views: `SeamTransactionView` (the ONE tx at the centre), `FinancialCrimeView`
  (L1 FATF, memo-blind), `AiSecurityView` (L2 vuln + `RegulatoryMappingView`,
  referenced not re-run), `SeamBindingView` (the thesis: shared tx id + signature),
  `ReportView` (FINnet draft+sign-off), `ArcView` (ordered stages + chain-integrity +
  the full ledger entries, so a saved run re-verifies its own hash chain offline).
  `RUN_RESULT_SCHEMA_VERSION` guards the on-disk shape.
- `keystone/demo/runner.py` — `build_run_result(*, narrate=None, signer, ledger=None)`
  runs the KS-0405 arc ONCE on a throwaway ledger (default) and assembles the
  run-result from real artifacts: re-derives the seam tx + FATF finding
  deterministically from the SAME seeded stream, asserts the binding is consistent
  (same tx id → `RunResultError` otherwise), and reads narrative/report/sign-off
  straight from the ledger it wrote. Offline by default (template narrative; no
  network). `save_run_result` / `load_run_result` round-trip via JSON;
  `run_json_path()` reads `KEYSTONE_RUN_JSON` (default `keystone-run.json`).
- `keystone/demo/__main__.py` — `python -m keystone.demo [path]`: build + save the
  golden-path run offline, print the binding + arc summary.
- `tests/test_demo_run_result.py` — both findings bind to the same seam tx; values
  come from the real run (canonical memo, signature fields, curated regulatory
  mapping) not hardcoded; arc whole/ordered/chain-valid; report drafted+signed+
  faithful; JSON round-trip equals (and re-verifies the chain); default-ledger clean
  arc; the CLI writes a loadable run.
- Realigned `docs/feature_list.json` Phase 5 (KS-0500–KS-0505 + depends_on edges),
  `ROADMAP.md`, `TASKS.md`.

## Decisions

- **A typed VIEW over the system of record, not a new source of truth.** The
  run-result is assembled from the ledger + deterministic re-derivation; it carries
  the full ledger entries so replay re-verifies the chain. No new detection.
- **Compose the milestone, don't fork it.** `build_run_result` calls the tested
  `run_layer1_milestone` for the authoritative arc and re-derives the typed objects
  the ledger payloads don't carry (tx amount/accounts, finding severity/signal).
  Determinism makes the two consistent; a mismatch raises rather than papering over.
- **Throwaway ledger by default.** One `build_run_result` call = one clean arc; the
  shared persistent ledger would accumulate stages and break the exact-arc check.
  `ignore_cleanup_errors=True` on the temp dir (the Ledger leaks open SQLite
  connections — a Windows unlink hazard; out of scope to fix here).
- **Regulatory mapping included now.** Imported verbatim from the curated assurance
  mapping (`FAMILY_MAPPINGS["promptinject"]`); real, and it pre-wires KS-0502 so the
  contract doesn't churn.
- **Boundary:** `keystone.demo` is the integration layer — imports core + assurance
  edge; the core never imports it (import-linter KEPT).

## Verification

- `make check` green OFFLINE — `demo/run_result.py` 100%, `runner.py` 91%
  (uncovered = defensive `RunResultError` branches), total 91.5%; 257 passed.
- `make verify` exit 0 — full suite; import-linter core→edge KEPT; feature_list valid.
- `python -m keystone.demo`: `seam tx: TXN-000016  signature: memo-instruction-injection
  typology: STRUCTURING`; `arc: ingested -> detected -> seam_bound -> reported -> signed
  chain_ok: True  entries: 5`. JSON round-trips equal.

## Next

KS-0501 — shared design system + the seam hero screen — renders from THIS run-result
(live via `build_run_result`, replay via `load_run_result`). Build it on a main that
has KS-0500 merged.
