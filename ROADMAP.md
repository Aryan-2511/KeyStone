# ROADMAP.md

> High-level phases. Each phase is a clean checkpoint — verify before advancing.
> The verifiable per-item breakdown lives in
> [`docs/feature_list.json`](docs/feature_list.json) (the source of truth);
> this file is the human-readable phase view.

## Phase 0 — Harness (current)

Tooling foundation only: src-layout, pyproject, strict gates (Ruff/mypy/pytest
coverage floor), pre-commit, CI, docs. **Done when `make check` is green.**
No application logic.

## Phase 1 — Chassis

- NAT YAML workflow skeleton (orchestration entry point).
- Hash-chained SQLite evidence ledger (deterministic core).
- Inference config switch (hosted NIM ↔ local Ollama).

> **Phases 2–5 are the three compliance layers — the product.** Build order is
> the phase number; each phase names the layer it delivers. Layer numbering (L1/L2/L3)
> is product meaning, not build order. See [`ADR-0011`](DECISIONS.md#adr-0011--realign-phases-25-to-the-three-compliance-layers).

## Phase 2 — Layer 3: Obligation Mapper

The first real layer; deterministic-heavy. (`KS-0201`–`KS-0205`)

- Curated obligation graph, ~25–30 nodes spanning EU AI Act Art. 9–15, DORA,
  India DPDP Act + DPDP Rules 2025, RBI responsible-AI guidance, PMLA/FIU-IND —
  **each node carries a source citation** (instrument + article/section). (`KS-0201`)
- Deterministic crosswalk/dedup onto a shared control library keyed to
  ISO/IEC 42001 + FATF + NIST AI RMF. (`KS-0202`)
- EU hard-law-conformity vs. India self-certification **modality contrast** as an
  explicit, surfaced attribute. (`KS-0203`)
- LLM used ONLY to phrase obligation summaries (core/edge boundary). (`KS-0204`)
- Citation-validation accuracy budget: the build fails on any unsourced or
  malformed node. (`KS-0205`)

## Phase 3 — Layer 2: AI Assurance Loop

Mock vulnerable agent + Guardrails + Garak. (`KS-0301`–`KS-0304`)

- Mock vulnerable payments agent, susceptible to indirect prompt injection. (`KS-0301`)
- NeMo Guardrails rails (input/output/dialog) at the LLM edge. (`KS-0302`)
- Garak probes wired as a subprocess against the deployed mock surface. (`KS-0303`)
- Milestone test (`-m milestone`) proving the end-to-end assurance loop. (`KS-0304`)

## Phase 4 — Layer 1: Transaction Monitor + the L2↔L1 seam

(`KS-0401`–`KS-0403`)

- Transaction Monitor: deterministic scoring over a synthetic transaction stream,
  findings to the ledger. (`KS-0401`)
- Planted fraudulent-transfer fixture entering via the **same** indirect-prompt-
  injection path Garak exercises in Phase 3. (`KS-0402`)
- **L2↔L1 seam** as one owned item: a `-m milestone` test asserting the fraud
  fixture's injection vector == the vector Garak flags, structurally (fails if a
  refactor decouples them). (`KS-0403`)

## Phase 5 — Integration & demo

(`KS-0501`–`KS-0503`)

- Posture dashboard (Streamlit) over the workflow and ledger. (`KS-0501`)
- Golden-path end-to-end run across all three layers. (`KS-0502`)
- Offline fallback so the demo runs without the hosted backend. (`KS-0503`)

_Out of scope throughout: Docker, tox, Sphinx, multi-version CI._
