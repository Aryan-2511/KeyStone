# ROADMAP.md

> High-level phases. Each phase is a clean checkpoint — verify before advancing.
> The verifiable per-item breakdown lives in
> [`docs/feature_list.json`](docs/feature_list.json) (the source of truth);
> this file is the human-readable phase view.

## Phase 0 — Harness

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

## Phase 2 — Layer 3: Obligation Mapper (current)

The first real layer; deterministic-heavy. (`KS-0201`–`KS-0206`)
KS-0201/0202/0204/0205/0206 are done; KS-0203 is next.

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
- Deterministic deontic-strength guard: phrasing falls back to the curated
  summary if it drifts binding↔advisory force (added during KS-0204 review;
  must precede `KS-0203`'s modality screen). (`KS-0206`)

## Phase 3 — Layer 2: AI Assurance Loop

Mock vulnerable agent + Guardrails + Garak. (`KS-0300` prerequisite, then `KS-0301`–`KS-0304`)

- Tool-calling inference seam: `complete_with_tools` + cross-backend argument
  normalization (a spike-found prerequisite; the mock agent `depends_on` it). (`KS-0300`)
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

(`KS-0500`–`KS-0505`) — narrative-first: two designed hero screens over a real
run-result, framed by a supporting shell.

- Demo runner + serializable run-result — the UI's typed contract over the
  Layer-1 arc (seam tx, both findings, the binding, report, hash-valid chain).
  (`KS-0500`)
- Shared design system + the **seam hero** — one transaction shown as both an
  AI-security vulnerability and a financial crime, bound on the shared id. (`KS-0501`)
- **Jurisdiction-contrast hero** — the same finding across EU vs India
  obligations. (`KS-0502`)
- Supporting shell — ledger, cross-layer posture, assurance before/after. (`KS-0503`)
- Recorded-run fallback so every screen replays offline. (`KS-0504`)
- Demo script + rehearsal — the narrated walkthrough. (`KS-0505`)

## Phase 6 — Movement 1: the Seam Matrix

(`KS-0601`–) — design contract: [`M1-00_SEAM_MATRIX_DESIGN.md`](M1-00_SEAM_MATRIX_DESIGN.md).
Generalise the single seam into a *characterized class*: a uniform framework that
binds (OWASP attack × FATF typology) pairs under one independence guarantee and one
build-failing drift assertion — including the honest boundary where the mapping does
not hold.

- The **seam framework abstraction** — bind any pair uniformly; P1 re-expressed as
  its first passing instance (the faithfulness proof). (`KS-0601` / M1-01)
- P2 rapid-movement, P3 large-transfer through the framework. (`KS-0602`+ / M1-02–03)
- P4 — the characterized **boundary** (data-loss moves no money → no typology
  fires; the negative is the result). (M1-04)
- P5 — the **open** pair (tool-misuse → recipient screening; reported CLEAN as-found,
  via a new standing recipient screen). (M1-05)
- The characterized-mapping result — the matrix as a RESULT (a `matrix` block on the
  RunResult + the third hero, a convergence figure). (M1-06)

> **Movement 1 is COMPLETE** (`KS-0601`–`KS-0606`). The characterized mapping:
> **4 CLEAN** (structuring / rapid-movement / large-transfer / unauthorized-recipient)
> **+ 1 BOUNDARY** (data-loss exfil), across two axes. See the figure at
> [`docs/assets/m1-06-matrix-hero.png`](docs/assets/m1-06-matrix-hero.png).

## Movement 2 — Regulatory Convergence

(`KS-0607`–) — design contract: [`M2-00_CONVERGENCE_DESIGN.md`](M2-00_CONVERGENCE_DESIGN.md).
Turn a seam event from *analogous* to a compliance failure into *being* the audit
evidence that satisfies-or-violates a named, real obligation — grounded in real
before/after data, across EU hard law + India advisory.

- The **evidence model** — a typed relationship binding a seam event to an existing L3
  obligation, with the four-part rigor as structure and a satisfy/violate state DERIVED
  from before/after (violated pre-patch → satisfied post-patch). Proven by one reference
  mapping (P1 × EU Art. 15). (`KS-0607` / M2-01)
- The rigorous obligation mappings (§4: ISO 42001 / NIST AI RMF / RBI + the DPDP
  boundary), each clearing the four-part bar. (`KS-0608` / M2-02)
- The convergence result + UI — the loop made visible. (M2-0n)

_Out of scope throughout: Docker, tox, Sphinx, multi-version CI._
