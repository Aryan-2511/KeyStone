<!--
Exec-plan (completed). KS-0302 — NeMo Guardrails patch that closes the memo hole.
-->

# Exec-plan: NeMo Guardrails patch (KS-0302)

- **Slug:** `guardrails-patch`
- **Feature IDs:** KS-0302 (Phase 3 / Layer 2). `depends_on` KS-0303 (reuses its
  Garak runner/parser as the verifier). Closes the KS-0301 vulnerability.
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-20
- **Owner (session):** agent
- **Branched from:** `main` @ d3de6f1 (KS-0303 merged).

## Why

The "patch" in find-and-patch: a real NeMo Guardrails rail that stops the KS-0301
memo-injection vulnerability, PROVEN by re-running the KS-0303 Garak detector
against the guarded agent — the probe that failed 10/12 must go clean.

## What shipped (`keystone.assurance`)

- `guardrails/` — a real NeMo Guardrails (v0.22) config: `config.yml` (input rail
  only), `rails.co` (Colang refuse flow), `actions.py` (thin `@action` shim). NO
  main LLM, NO embedding model → `models=[]`, constructs offline, nothing downloads.
- `injection_patterns.py` — typed, unit-tested `is_data_field_injection`: detects
  instruction-override / echo / fake-turn / settlement-directive patterns. Tuned on
  the probe's full 256-prompt set: 256/256 attacks blocked, 0 benign over-blocks.
- `guard.py` — `is_blocked` (input-only rail, reads `activated_rails` stop) and
  `run_guarded_agent` (the wrapper patch: vet the memo, refuse on a hit, else run
  the normal agent). Keeps nemoguardrails out of `agent.py`.
- `garak_endpoint.py` — serves the guarded brain over HTTP (Garak's isolated venv
  can't import nemoguardrails) + `scan_guarded_agent` (Garak `rest` generator).
- `garak_probe.record_remediation` — the `vulnerability_remediated` ledger entry.
- Fixture `latentinjection_guarded.report.jsonl` (fails 0/12) + `tests/test_guardrails_patch.py`.

## Decisions

- **Deterministic input rail, not an LLM/embedding rail** — the 4 GB box can't pull
  models, and the flaw (instruction-in-data) is pattern-detectable. Real NeMo
  Guardrails orchestrates it (not a hand-rolled if).
- **Vet the untrusted memo, not the user command** — so a legitimate transfer
  (benign memo, authorized by command) is not over-blocked; only data-field
  instructions are refused.
- **`@action` untyped decorator** → scoped mypy relaxation for ONLY the shim module
  (NeMo analog of ADR-0010); the security logic stays fully typed.
- **Guarded re-scan via HTTP `rest`** because the `function` target (KS-0303) can't
  carry nemoguardrails into Garak's venv.

## Verification

- `make check` green OFFLINE (no Garak/Ollama/network) — guard + injection_patterns
  100%, total 89.5%.
- `make verify` exit 0 — 195 passed / 2 skipped; import-linter core→edge KEPT;
  no core data changed; pip-audit clean.
- **Find-and-patch proof:** unguarded Garak `fails 10/12 (0.83)` → guarded
  `fails 0/12 (0.00)`, `found_our_vulnerability` False. Benign + legit transfers
  still work (fast tests). Sample remediation ledger entry: `{action:
  vulnerability_remediated, control: nemo-guardrails-input-rail, before_fails: 10,
  after_fails: 0, remediated: true}`.

## Honest scope

The rail FULLY closes THIS authored vulnerability. Real-world guardrailing is
defense-in-depth, not a silver bullet — a single deterministic input rail is the
demo's patch, not a general prompt-injection cure (MEMORY.md).

## Next

KS-0304 — the end-to-end assurance-loop milestone (`-m milestone`): ingest →
guard/finding → ledger, asserting the verifiable chain found → patched → closed.
