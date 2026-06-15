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

## Next — Phase 2 = Layer 3: Obligation Mapper (do NOT start yet)

> Phases 2–5 are realigned to the three compliance layers (ADR-0011). Full
> verifiable breakdown in `docs/feature_list.json`.

- [ ] Curated obligation graph, ~25–30 nodes (EU AI Act Art. 9–15, DORA, India
      DPDP Act + DPDP Rules 2025, RBI, PMLA/FIU-IND), each with a source citation — KS-0201
- [ ] Deterministic crosswalk/dedup onto a shared control library (ISO/IEC 42001
      + FATF + NIST AI RMF) — KS-0202
- [ ] EU hard-law vs India self-certification modality contrast (surfaced attribute) — KS-0203
- [ ] LLM-edge obligation-summary phrasing only (core/edge boundary) — KS-0204
- [ ] Citation-validation accuracy budget (build fails on unsourced/malformed node) — KS-0205

## Later phases

- [ ] Phase 3 — Layer 2: AI Assurance Loop (mock vulnerable agent + Guardrails +
      Garak + milestone) — KS-0301–KS-0304
- [ ] Phase 4 — Layer 1: Transaction Monitor + the L2↔L1 seam milestone — KS-0401–KS-0403
- [ ] Phase 5 — Integration & demo (posture dashboard, golden path, offline fallback) — KS-0501–KS-0503
