<!--
Exec-plan (completed). KS-0304 — Layer-2 assurance-loop milestone, NAT-orchestrated.
-->

# Exec-plan: Assurance-loop milestone (KS-0304)

- **Slug:** `assurance-milestone`
- **Feature IDs:** KS-0304 (Phase 3 / Layer 2). `depends_on` KS-0301 + KS-0302 +
  KS-0303 — composes them. **Completes Layer 2.**
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-20
- **Owner (session):** agent
- **Branched from:** `main` @ 7259f36 (KS-0302 merged).

## Why

Prove the "orchestrated by NeMo Agent Toolkit" claim by composing the existing
Layer-2 pieces into ONE end-to-end find-and-patch loop the NAT runtime drives,
writing the full arc to the evidence ledger. Build nothing new in capability.

## Step-1 spike findings (NAT had never run end-to-end beyond the Phase-1 stubs)

- NAT drives our real stages cleanly (ran the live agent + a ledger read via the
  chassis fan-out pattern). Config format unchanged from Phase 1.
- **Surprise:** NeMo Guardrails' sync `rails.generate` raises inside NAT's async
  event loop. Fix: the NAT `_run` runs the synchronous loop via
  `await asyncio.to_thread(run_assurance_loop, ...)` (worker thread has no loop).
- State between stages flows through the ledger; no heavy model needed; NAT still
  logs a non-fatal `langchain_core`/`nvidia_rag` auto-discovery import error.

## What shipped

- `keystone/assurance/loop.py` — the pure SPINE: `LoopDeps` (injected stages),
  `run_assurance_loop` (5 ordered stages → `assurance_loop_stage` ledger entries),
  `assert_assurance_arc` (the milestone check: ARC in order + hash-valid).
- `keystone/assurance/loop_live.py` — `live_deps` wiring the real KS-0301/0303/0302
  components (kept separate so the spine + fast tests stay nemoguardrails-free).
- `keystone/agents/orchestrator/` — `AssuranceLoopConfig` + `build_assurance_loop`
  (a registered NAT workflow function) + `assurance_workflow.yml`;
  `run.py:run_milestone`/`main_milestone`; `make milestone`.
- `tests/test_assurance_loop.py` — fast spine over canned deps (arc in order,
  evidence per stage, missing/out-of-order FAIL, NAT config loads) + a slow
  `@milestone` live loop via NAT.

## Decisions

- **NAT is the driver** (load_workflow → session.run → the registered workflow
  function → the loop), not a script importing NAT. Spike-confirmed.
- **Spine/live split** so the fast gate runs the EXACT sequencing over canned
  results with no live deps; only the milestone pulls Garak/Ollama/nemoguardrails.
- **`asyncio.to_thread`** bridges the sync loop into NAT's async `_run` (the NeMo
  sync-generate-in-async constraint). No code rewrite, no new ADR.

## Verification

- `make check` green OFFLINE (canned spine, no live deps) — loop.py 99%, total 88.9%.
- `make verify` exit 0 — 202 passed / 2 skipped; import-linter core→edge KEPT; no
  core data changed; pip-audit clean.
- **`make milestone` (live, NAT-orchestrated):**
  `exploit before=True after=False | garak fails before=11 after=0 |
  remediated=True arc_complete=True`; `ledger arc: exposed -> detected -> mapped ->
  patched -> verified`; `6 entries, chain_ok=True`.

## Next

Layer 2 is COMPLETE. Phase 4 / Layer 1 — Transaction Monitor + the L2↔L1 seam
(KS-0401–0403); the seam reuses `MEMO_INJECTION_SIGNATURE` (the planted fraud
vector == the Garak-flagged vector).
