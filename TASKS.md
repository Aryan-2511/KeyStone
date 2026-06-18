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

## Now — Phase 2 = Layer 3: Obligation Mapper (in progress; KS-0203 next)

> Phases 2–5 are realigned to the three compliance layers (ADR-0011). Full
> verifiable breakdown in `docs/feature_list.json`.

- [x] Curated obligation graph, 28 nodes (EU AI Act Art. 9–15, DORA, India
      DPDP Act + DPDP Rules 2025, RBI, PMLA/FIU-IND), each with a source citation — KS-0201
      (`keystone.core.obligations`, `tests/test_obligations.py`)
- [x] Deterministic crosswalk/dedup onto a shared control library (ISO/IEC 42001
      + FATF + NIST AI RMF) — KS-0202 (`keystone.core.controls`, 15 controls;
      §5b validator `scripts/validate_controls.py`, `tests/test_controls.py`)
- [ ] EU hard-law vs India self-certification modality contrast (surfaced attribute) — KS-0203
- [x] LLM-edge obligation-summary phrasing only (core/edge boundary) — KS-0204
      (`keystone.llm.phrasing.phrase_summary`, NIM no-think; `tests/test_phrasing.py`)
- [x] Citation-validation accuracy budget (build fails on unsourced/malformed node) — KS-0205
      (`scripts/validate_obligations.py`, wired into `make verify`)
- [x] Deterministic deontic-strength guard: phrasing falls back to the curated
      summary on binding↔advisory drift — KS-0206 (`keystone.core.deontic`,
      `keystone.llm.phrasing`; must precede KS-0203's modality screen)

## Later phases

- [ ] Phase 3 — Layer 2: AI Assurance Loop (mock vulnerable agent + Guardrails +
      Garak + milestone) — KS-0301–KS-0304
- [ ] Phase 4 — Layer 1: Transaction Monitor + the L2↔L1 seam milestone — KS-0401–KS-0403
- [ ] Phase 5 — Integration & demo (posture dashboard, golden path, offline fallback) — KS-0501–KS-0503

## Backlog — hygiene / tech-debt (not scheduled; not features)

> Tracked so they aren't lost. Revisit on the noted trigger; none block KS-0202.

- [ ] **CI: bump GitHub Actions off Node 20.** `actions/checkout@v4` and
      `astral-sh/setup-uv@v6` in `.github/workflows/ci.yml` run on the
      deprecated Node 20 runtime; move to the Node 24-based major versions when
      convenient. (CI hygiene only — no behaviour change.)
- [ ] **Drop the cryptography override (ADR-0013).** Remove
      `[tool.uv] override-dependencies = ["cryptography>=48.0.1"]` from
      `pyproject.toml` once a stable `nvidia-nat` ships an `nvidia-nat-core`
      whose declared `cryptography` constraint allows `>=48` (re-check
      `nat-core`'s `requires_dist` on the next bump). See `DECISIONS.md` ADR-0013.
