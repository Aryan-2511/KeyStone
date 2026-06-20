<!--
Exec-plan (completed). KS-0402 — FATF typology detection engine (memo-blind).
-->

# Exec-plan: FATF typology engine (KS-0402)

- **Slug:** `fatf-engine`
- **Feature IDs:** KS-0402 (Phase 4 / Layer 1). `depends_on` KS-0401 (detects over
  its stream). Detection only — no seam (KS-0403), no signature import.
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-21
- **Owner (session):** agent
- **Branched from:** `main` @ 1806ae5 (KS-0401 merged).

## Why

Layer 1 needs deterministic financial-crime detection over the synthetic stream.
Crucially it must be MEMO-BLIND so the KS-0403 seam's two detections (AML here,
prompt-injection in the assurance loop) are genuinely independent.

## What shipped (`keystone.core.fatf`, deterministic core)

- `models.py` — `Typology` (STRUCTURING / RAPID_MOVEMENT / LARGE_TRANSFER),
  `Severity`, and `Finding {typology, severity, account, transaction_ids, signal
  (financial only — NO memo), rationale}`.
- `engine.py` — `FatfThresholds` (named, configurable: ctr=10000, band_floor=5000,
  structuring_min=3/window=24h, rapid_min=5/window=1h), `detect` (three rules over a
  sliding two-pointer densest-window), and `record_findings` → ledger (agent
  `fatf-monitor`, layer `L1`, action `fatf_finding`). NOTHING reads `.memo`.
- `tests/test_fatf.py` — cluster caught (correct ids), benign clean (0 FP), the
  thesis-critical memo-blindness test, threshold boundary, min-transfers, ledger
  shape, determinism, configurable thresholds.

## Decisions

- **Memo-blindness is enforced two ways:** the rules only read amount/timing/
  accounts/type, AND a test asserts blank-vs-filled memos give identical findings.
  This is the invariant the KS-0403 "same gap, two independent detections" thesis
  rests on.
- **Named thresholds, not magic numbers** — `FatfThresholds` is a frozen dataclass;
  the cluster's separation from benign traffic is wide, so the defaults are
  defensible (benign max transfer ~$2.9k; cluster all in [$9.0k, $9.8k]).
- **The cluster is caught by TWO typologies** (structuring + rapid movement) — a
  credible engine result, not forced.

## Verification

- `make check` green — fatf models/engine 100% covered, total 90.8%.
- `make verify` exit 0 — 229 passed / 2 skipped; import-linter core→edge KEPT (pure
  core, no LLM-edge import); no existing core data changed.
- On `sample_stream()`: **2 findings, both ACC-0004** — STRUCTURING (9 transfers,
  $85,417.57 total, 51 min) + RAPID_MOVEMENT (9 transfers, 3 recipients) — and
  **zero false positives** on the benign portion; LARGE_TRANSFER fires 0×.

## Next

KS-0403 — the L2↔L1 seam milestone: plant `CANONICAL_MEMO_EXPLOIT` in a
transaction's memo; assert (structurally) its injection vector == the
Garak-flagged vector, while THIS engine catches the same transfer on AML grounds.
