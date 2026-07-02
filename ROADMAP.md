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

## Phase 2 — Layer 3: Obligation Mapper — DONE

The first real layer; deterministic-heavy. (`KS-0201`–`KS-0206`)
All of `KS-0201`–`KS-0206` are done (see `docs/feature_list.json`, the source of
truth). Work has since moved through Layers 2/1 and Movements 1, 2, A and B.

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
- The rigorous obligation mappings (`REGISTERED_MAPPINGS`): EU Art.15 + Art.9 (hard law),
  RBI Sutra 1 (advisory) — ISO 42001 + NIST surfaced via the control spine — and the DPDP
  data-protection boundary (NOT_EVIDENCED by fund movement). (`KS-0608` / M2-02)
- The convergence result + UI — the loop made visible: the same event violated→satisfied
  across EU + India, with the DPDP boundary and the honest disclaimer. (`KS-0609` / M2-0n)

> **Movement 2 is COMPLETE** (`KS-0607`–`KS-0609`). Regulatory convergence as a feature:
> a seam event IS the audit evidence that takes named obligations from violated to
> satisfied, across EU hard law + India advisory, with an honest data-protection boundary.
> See the figure at [`docs/assets/m2-0n-convergence-hero.png`](docs/assets/m2-0n-convergence-hero.png).

## Movements A/B — a multi-agent system (DONE)

Keystone is an **orchestrated** assurance workflow with a **deterministic-by-design** core
(NAT sequences fixed stages; the FATF detection, the seam binding, and the hash-chained
ledger are deterministic where auditability demands it) — and, as of MB-01, a genuine
**multi-agent** edge: two agents that reason and choose, in a supervisor–worker topology.
The honest path that got here (probes: `agentic_audit.md`, `multi_agent_feasibility.md`;
designs: `MA-00_REDTEAM_AGENT_DESIGN.md`, `MB-00_TRIAGE_AGENT_DESIGN.md`):

- **Movement A — the Red-Team Agent** (`MA-01`, `KS-0612`) — **DONE.** The first genuine
  agent: `keystone.agents.red_team` observes each probe's outcome and adapts its next
  choice over the 23-probe Garak prompt-injection space, its attack sequence a function of
  observed defenses. Shipped as **Option B — an adaptive offensive policy**, framed honestly
  (an agent by the §2 bar — the next action depends on observation — but it reasons via an
  explicit policy, NOT an LLM; Option A is a later upgrade). The §2 honesty test passes
  (flip the observations → the probe sequence flips). Record/replay (schema v6) preserves
  the offline default + deterministic demo; the memo-blind boundary holds with the agent in
  the loop. **Keystone now has one genuine agent — still not yet multi-agent (that needs MB).**
- **Movement B — the Triage Agent** (`MB-01`, `KS-0613`) — **DONE.** The second genuine
  agent: `keystone.agents.triage` routes a finding (remediate / accept / escalate) over the
  INTERPLAY of its already-computed signals (failure_rate, seam_result, severity), its route
  a function of how they COMBINE — the same failure_rate routes differently by seam context
  (CLEAN → remediate, BOUNDARY → accept, OPEN → escalate). Shipped as **Option B — an
  adaptive triage policy**, framed honestly (an agent by the §2 bar — the route depends on
  the observed combination, ≥2 genuine options — but it reasons via an explicit policy, NOT
  an LLM; Option A is a later upgrade). The §2 interplay honesty test passes; all three
  routes are reachable. "remediate" is a ROUTE, not a fix-selection (that is gated Movement
  C). Record/replay (schema v7) preserves the deterministic demo; the memo-blind boundary
  holds with BOTH agents in the loop. **A + B = a multi-agent system — now TRUE.**
- **(Later) Movement C**: a defense agent — gated on a real ≥2-remediation menu (a single
  rail is one choice, not an agent).

> **Keystone is now honestly MULTI-AGENT** (as of MB-01): two genuine agents in a
> supervisor–worker topology — the Red-Team Agent (offensive worker) produces findings; the
> Triage Agent (supervisor) routes them — each passing the strict §2 agency bar, verifiable
> by reading the code. The present-tense "multi-agent system" claim is now defensible.

_Out of scope throughout: Docker, tox, Sphinx, multi-version CI._
