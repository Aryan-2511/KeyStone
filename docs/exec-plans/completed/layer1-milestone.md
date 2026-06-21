<!--
Exec-plan (completed). KS-0405 — Layer-1 milestone (NAT-orchestrated), closing the seam to L2.
-->

# Exec-plan: Layer-1 milestone (KS-0405)

- **Slug:** `layer1-milestone`
- **Feature IDs:** KS-0405 (Phase 4 / Layer 1). `depends_on` KS-0401/0402/0403/0404.
  **Completes Layer 1 and the three-layer core build.**
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-21
- **Owner (session):** agent
- **Branched from:** `main` @ a782aab (KS-0404 merged).

## Why

Compose the existing Layer-1 pieces into one end-to-end NAT-orchestrated run that
closes the seam to L2: stream → FATF catches fraud → the caught tx is shown to
carry the SAME signature L2 found/patched → report drafted → human signs → full
auditable chain. Reference the proven L2 finding; do NOT re-run the assurance loop.

## What shipped

- `keystone/assurance/layer1_milestone.py` — the SPINE: `Layer1Stage`/`ARC`,
  `run_layer1_milestone(*, narrate, signer, ledger)` (5 ordered stages →
  `layer1_milestone_stage` ledger entries; the SEAM stage binds the FATF-flagged tx
  to `MEMO_INJECTION_SIGNATURE` by identity + an `l2_reference` citing KS-0304's
  found+patched, NOT re-run), `assert_layer1_arc`. LLM narrative INJECTED.
- `keystone/assurance/layer1_live.py` — `live_narrate` (the real LLM edge), kept
  apart so the spine + fast tests need no Ollama.
- `keystone/agents/orchestrator/` — `Layer1MilestoneConfig` + `build_layer1_milestone`
  (registered NAT workflow fn, `asyncio.to_thread` for the sync arc) +
  `layer1_workflow.yml`; `run.py:run_layer1`/`main_layer1_milestone`;
  `make layer1-milestone`.
- `tests/test_layer1_milestone.py` — fast spine over a canned narrative (arc in order,
  seam→L2 binding, missing/out-of-order FAIL, FINnet report carried, fall-back
  propagation, the drift guard, NAT config loads) + a slow `@milestone` live arc via NAT.

## Decisions

- **Reference, don't re-run** (the scope decision): the SEAM stage resolves the memo
  to the canonical signature (single source, `is`-identity) and cross-references the
  L2 finding in the ledger. No Garak/Guardrails/loop re-run.
- **NAT is the driver** (mirrors KS-0304): a registered workflow fn run via
  `load_workflow` + `session.run`; `asyncio.to_thread` bridges the sync arc into NAT's
  async `_run`.
- **Spine/live split** (mirrors loop.py/loop_live.py) so the fast gate exercises the
  exact sequencing over a canned narrative — no live deps. State flows via the ledger.
- **Boundary:** the milestone is edge (`keystone.assurance`), importing the seam +
  signature + core + the narrative type. Core never imports it; import-linter KEPT.

## Verification

- `make check` green OFFLINE — milestone spine 97%, total 91.2%.
- `make verify` exit 0 — 258 passed / 2 skipped; import-linter core→edge KEPT; no core
  data changed.
- **`make layer1-milestone` (live, NAT-orchestrated):** `fraud tx=TXN-000016
  (STRUCTURING) | seam -> L2 signature=memo-instruction-injection | report
  signed_by=compliance.officer@keystone (narrative_fell_back=False) | arc_complete=True`;
  `arc: ingested -> detected -> seam_bound -> reported -> signed`; 5 entries, chain ok.

## Next

The three-layer core build is COMPLETE (Layers 3/2/1 + the L2↔L1 seam + reporting +
both milestones). Remaining is Phase 5 — integration & demo (posture dashboard,
golden path, offline fallback, KS-05xx).
