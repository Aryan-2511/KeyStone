<!--
Exec-plan (completed). KS-0301 — mock vulnerable payments agent (vulnerable by design).
-->

# Exec-plan: Mock vulnerable payments agent (KS-0301)

- **Slug:** `mock-agent`
- **Feature IDs:** KS-0301 (Phase 3 / Layer 2). `depends_on` KS-0300 (the
  tool-calling seam), now satisfied. Precedes KS-0302 (Guardrails) and KS-0303
  (Garak), which probe/patch this agent.
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-19
- **Owner (session):** agent
- **Branched from:** `main` @ 17444cd (KS-0300 merged).

## Why

Layer 2 needs a target surface for Garak to probe and Guardrails to patch. The
spike proved a well-aligned model resists a naive injection (0/10) but a
vulnerable-by-design agent fires it 10/10. So the vulnerability must be built into
the agent's architecture, not hoped for from the model.

## What shipped (`keystone.assurance`)

- `signature.py` — the SINGLE SOURCE OF TRUTH for the planted flaw: typed enums
  (`InjectionField.MEMO`, `InjectionMechanism.INSTRUCTION_IN_DATA`,
  `ExploitOutcome.UNAUTHORIZED_INITIATE_TRANSFER`), `VulnerabilitySignature`
  (`MEMO_INJECTION_SIGNATURE`, `exploit_tool="initiate_transfer"`), and the FIXED
  `CANONICAL_MEMO_EXPLOIT`. Both the future Garak probe (KS-0303) and the L1 fraud
  fixture (KS-0403) import this — the structural L2↔L1 seam.
- `agent.py` — `run_agent(transaction, *, backend=None, ledger=None) -> AgentRun`
  on the KS-0300 seam (`complete_with_tools`), two tools (`lookup_balance` stub,
  `initiate_transfer` STUB), the vulnerable-by-design `VULNERABLE_SYSTEM_PROMPT`
  (trusts the memo as instructions), `initiate_transfer` → ledger `transfer_intent`
  entry tagged with the memo that triggered it, and `exploit_fired(run)` (binary:
  any `exploit_tool` call). `initiate_transfer` performs NOTHING real.
- `tests/test_mock_agent.py` — fast (canned seam, no Ollama): benign behaves +
  clean ledger, memo-injection fires + records intent, ledger entry shape (trigger
  == memo), signature well-formed + example matches, non-numeric amount, chain
  integrity. Slow: live 10-trial exploit on qwen2.5:3b (skips if Ollama down).

## Decisions

- **Vulnerability is architectural** (system prompt + tool-wiring), fixed and known
  (one canonical malicious memo) so the demo reproduces every run — no adversarial
  prompt cleverness.
- **`initiate_transfer` is a pure stub → ledger intent only.** The ledger entry is
  the artifact L1 detects as fraud; the agent never moves money.
- **Signature is typed + importable, not literal bytes** — the example carries the
  payload, the signature carries the structure. No new ADR (implements the ADR-0011
  L2↔L1 seam intent).
- Lives in `keystone.assurance` (edge scaffolding), calls core (ledger) + edge
  (llm.inference); import-linter core→edge KEPT.

## Verification

- `make check` green WITHOUT Ollama (canned backend), assurance 96–100% cov.
- `make verify` exit 0 — 172 passed / 2 skipped (NIM live, no key); import-linter
  KEPT; no core data files changed.
- **Live exploit hit rate: 10/10** on qwen2.5:3b (`-m slow`), matching the spike.
- Sample ledger intent (live): `{agent: mock-payments-agent, layer: L2,
  action: transfer_intent, payload: {amount: 9999.0, recipient: ATTACKER-999,
  source_field: memo, trigger: "<malicious memo>", signature:
  memo-instruction-injection}}`.

## Next

KS-0302 — NeMo Guardrails rails around this agent (input/output/dialog), then
KS-0303 — Garak probing the same surface using `CANONICAL_MEMO_EXPLOIT`.
