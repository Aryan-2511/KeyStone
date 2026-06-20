<!--
Exec-plan (completed). KS-0401 — transaction model + synthetic stream (Layer-1 substrate).
-->

# Exec-plan: Transaction substrate (KS-0401)

- **Slug:** `transaction-substrate`
- **Feature IDs:** KS-0401 (Phase 4 / Layer 1). The data layer all of Layer 1
  operates on. Re-scoped within Phase 4: KS-0401 is the SUBSTRATE; detection moves
  to KS-0402 (FATF typology engine); KS-0403 is the seam.
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-21
- **Owner (session):** agent
- **Branched from:** `main` @ 5bdcae5 (KS-0304 merged, Layer 2 complete).

## Why

Layer 1 needs a typed transaction + a deterministic synthetic generator before any
detection or seam. KS-0401 builds only the substrate, shaped so the settled seam
contract (KS-0403) is possible: a memo injection locus AND independently-suspicious
financial behaviour.

## What shipped (`keystone.core.transactions`, deterministic core)

- `models.py` — `Transaction` (Pydantic v2, frozen, extra=forbid): id `TXN-NNNNNN`,
  timestamp, sender/recipient `ACC-NNNN`, amount>0, `Currency`, `TransactionType`,
  and a free-text `memo` (default ""). Fail-loud validators (id/account patterns,
  positive amount, no self-transfer) mirror obligations/ledger.
- `generator.py` — `StreamConfig` (seeded) + `generate_stream` (normal traffic +
  opt-in `structuring_clusters`), `structuring_cluster` (one sender, ≥6 transfers
  each just under `STRUCTURING_THRESHOLD`=10000, minutes apart = FATF smurfing +
  rapid movement), and `sample_stream()` (canonical fixture: 30 normal + 1 cluster).
  Labels NOTHING as fraud.
- `tests/test_transactions.py` — model round-trip + fail-loud (parametrized),
  memo-carries-arbitrary-text (seam locus, signature NOT imported), generator
  determinism, structuring-cluster emission, sample-stream reproducibility.

## Decisions

- **Substrate only** — no fraud detection (KS-0402), no signature import / planted
  exploit (KS-0403). Held the line per the task.
- **Memo + structuring are BOTH present on purpose** so the KS-0403 seam is
  catchable two independent ways (injection vector AND money pattern).
- **Seeded `random.Random`** with a scoped `# noqa: S311` — reproducibility is the
  requirement; a CSPRNG can't be seeded. Not security; documented inline.
- Fixture is a deterministic `sample_stream()` function (no committed JSON / loader)
  — the generator is the source of truth, so a data file would only risk drift.

## Verification

- `make check` green — transactions models/generator 100% covered, total 90%.
- `make verify` exit 0 — 219 passed / 2 skipped; import-linter core→edge KEPT (the
  package is pure core, no LLM-edge import); no existing core data changed.
- Sample structuring cluster (from `sample_stream()`): ACC-0004 made 9 transfers of
  $9,011–$9,846 (all under the $10k threshold) within ~50 min to 3 recipients, with
  benign memos — independently suspicious on financial-crime grounds.

## Next

KS-0402 — the FATF typology engine: detect the structuring/rapid-movement pattern
over the stream and append a verifiable finding to the ledger. Then KS-0403 — the
L2↔L1 seam (plant `CANONICAL_MEMO_EXPLOIT` in a transaction's memo; assert its
vector == the Garak-flagged vector).
