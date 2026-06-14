# TASKS.md

> Human-readable task view. The **machine-checkable source of truth** is
> [`docs/feature_list.json`](docs/feature_list.json) (validated in CI); agents
> check work against that. Keep this file as the readable summary.

## Done

- [x] **Phase 0 — Harness.** src-layout, strict gates, pre-commit/CI, docs,
      feature-list + validator, verification loop, import-linter, continuity.
- [x] **Phase 1 — Chassis (skeleton).** All `make check` / `make phase-check` /
      `make demo` green.
  - [x] Hash-chained SQLite evidence ledger (`keystone.core.ledger`) — KS-0102/0103
  - [x] Inference switch nim/ollama (`keystone.llm.inference`) — KS-0104
  - [x] NAT workflow skeleton + orchestrator + run entrypoint
        (`keystone.agents.orchestrator`, `keystone.agents.run`) — KS-0101
  - [x] Streamlit shell (`keystone.ui.app`, `make demo`)
  - [x] Ledger unit tests + `@milestone` integration test (3 layers + chain)

## Next (Phase 2 — do NOT start yet)

- [ ] Compliance/assurance agents on the NAT workflow — KS-0201
- [ ] NeMo Guardrails rails (input/output/dialog) — KS-0202
