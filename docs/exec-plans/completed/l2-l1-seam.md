<!--
Exec-plan (completed). KS-0403 — the L2↔L1 seam (thesis-closing milestone).
-->

# Exec-plan: L2↔L1 seam (KS-0403)

- **Slug:** `l2-l1-seam`
- **Feature IDs:** KS-0403 (Phase 4 / Layer 1). `depends_on` KS-0401 + KS-0402 +
  KS-0303 (all in main). The thesis-closing milestone.
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-21
- **Owner (session):** agent
- **Branched from:** `main` @ eda98ea (KS-0402 merged).

## Why

Close the "same gap, two independent detections" thesis: ONE transaction that is
both a financial crime (caught by the memo-blind FATF engine) AND an AI-security
vulnerability (its memo carries the canonical injection the assurance loop flags),
bound on a shared transaction id.

## What shipped (`keystone.assurance.seam`, edge)

- `resolve_signature(memo)` — reuses the KS-0302 `is_data_field_injection` detector
  and returns `CANONICAL_MEMO_EXPLOIT.signature` (which **is** `MEMO_INJECTION_SIGNATURE`).
  Composition only; no new detection, no redefined signature.
- `seam_fraud_stream()` — plants `CANONICAL_MEMO_EXPLOIT.memo` into ONE transfer of
  the KS-0401 sample structuring cluster (found via the memo-blind FATF engine,
  before planting). Returns the stream + the seam tx id (`TXN-000016`).
- `prove_seam(ledger=...)` → `SeamProof{transaction_id, fatf_finding, signature}`;
  raises `SeamError` if either side stops implicating the seam tx (the drift guard).
  Writes a Layer-1 `fatf_finding` + a `seam_binding` ledger entry (agent `l2-l1-seam`,
  layer `L1+L2`) naming the same tx id and the signature.
- `tests/test_seam.py` — the `@milestone` strong assertion (same tx id, both
  detections, `signature is MEMO_INJECTION_SIGNATURE`), memo-IS-canonical, memo-blind
  AML on the seam fraud, ledger binding, and the fail-loud drift guard.

## Decisions

- **Strong binding on a shared transaction id**, not just signature-exists-twice:
  `seam_tx_id in fatf_finding.transaction_ids` AND `resolve_signature(seam.memo) is
  MEMO_INJECTION_SIGNATURE`. One event, two findings.
- **Single source of truth** — import the signature/exploit; the `is` identity check
  is the drift guard (a copy would fail it).
- **Relied on KS-0402's memo-blindness** (did NOT make FATF memo-aware): a test blanks
  the seam memo and shows the FATF findings are identical — the independence the thesis
  needs.
- **Boundary:** seam in `keystone.assurance` (edge), importing the assurance signature
  + `keystone.core.transactions`/`keystone.core.fatf` (core). Core never imports it —
  import-linter KEPT.

## Verification

- `make check` green — seam.py 96% (the one uncovered line is the unreachable
  fail-loud guard), total 90.8%.
- `make verify` exit 0 — 236 passed / 2 skipped; import-linter core→edge KEPT; no
  core data changed.
- **The seam binds:** seam tx `TXN-000016` — Layer 1 FATF flags it STRUCTURING
  (implicates the id), Layer 2 its memo resolves to `memo-instruction-injection`
  (`is` the canonical object), `memo_is_canonical_exploit: true`, chain valid.

## Next

The thesis is closed (Layers 1/2/3 + the L2↔L1 seam). Remaining is Phase 5 —
integration & demo (posture dashboard, golden path, offline fallback, KS-05xx).
