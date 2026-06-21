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

## Now — Phase 2 = Layer 3: Obligation Mapper (in progress; next → Layer 2 / KS-03xx)

> Phases 2–5 are realigned to the three compliance layers (ADR-0011). Full
> verifiable breakdown in `docs/feature_list.json`.

- [x] Curated obligation graph, 28 nodes (EU AI Act Art. 9–15, DORA, India
      DPDP Act + DPDP Rules 2025, RBI, PMLA/FIU-IND), each with a source citation — KS-0201
      (`keystone.core.obligations`, `tests/test_obligations.py`)
- [x] Deterministic crosswalk/dedup onto a shared control library (ISO/IEC 42001
      + FATF + NIST AI RMF) — KS-0202 (`keystone.core.controls`, 15 controls;
      §5b validator `scripts/validate_controls.py`, `tests/test_controls.py`)
- [x] EU hard-law vs India self-certification modality contrast (surfaced attribute) — KS-0203
      (`keystone.ui.modality_view`: deterministic view-model = Phase-5 UI data contract;
      `has_modality_contrast` first-class on CTL-GOV-01 + CTL-TRANSP-01; `tests/test_modality_view.py`)
- [x] LLM-edge obligation-summary phrasing only (core/edge boundary) — KS-0204
      (`keystone.llm.phrasing.phrase_summary`, NIM no-think; `tests/test_phrasing.py`)
- [x] Citation-validation accuracy budget (build fails on unsourced/malformed node) — KS-0205
      (`scripts/validate_obligations.py`, wired into `make verify`)
- [x] Deterministic deontic-strength guard: tiered classifier + enforcement_modality
      cross-check; phrasing falls back to the curated summary on STRONG-strength
      drift or a hard-law node read advisory — KS-0206 (`keystone.core.deontic`,
      `keystone.llm.phrasing`; ~7% of nodes fall back; precedes KS-0203's screen)

## Later phases

- [x] Tool-calling inference seam (`complete_with_tools` + cross-backend
      normalization; arguments dict-vs-string → one canonical `ToolCallResult`) —
      KS-0300 (`keystone.llm.inference`, `tests/test_inference_tools.py`; the
      spike-discovered Phase-3 prerequisite the mock agent `depends_on`)
- [x] Mock vulnerable payments agent, vulnerable BY DESIGN (memo trusted as
      instructions → unauthorized `initiate_transfer` stub → ledger intent) +
      canonical `VulnerabilitySignature` the Garak probe & L1 fixture import —
      KS-0301 (`keystone.assurance`, `tests/test_mock_agent.py`; live exploit 10/10)
- [x] Garak red-team as isolated subprocess (v0.15.1): finds the memo-injection
      vuln, parses JSONL → typed findings → OWASP/Art.15/India mapping → ledger
      finding — KS-0303 (`keystone.assurance.garak_probe`,
      `tests/test_garak_probe.py`; built BEFORE KS-0302, detector-before-patch)
- [x] NeMo Guardrails patch (v0.22): deterministic input rail closes the
      memo-injection hole — Garak re-scan goes 10/12 → 0/12, benign+legit flows
      intact, remediated finding to ledger — KS-0302 (`keystone.assurance.guard`,
      `tests/test_guardrails_patch.py`; `depends_on` KS-0303 satisfied)
- [x] **Layer 2 COMPLETE** — assurance-loop milestone orchestrated by NeMo Agent
      Toolkit: exposed → detected → mapped → patched → verified, full hash-valid
      ledger arc; `make milestone` runs it live — KS-0304
      (`keystone.assurance.loop`, `keystone.agents.orchestrator`,
      `tests/test_assurance_loop.py`)

## Phase 4 = Layer 1: Transaction Monitor + the L2↔L1 seam — COMPLETE (three-layer core build done)

- [x] Transaction substrate: typed `Transaction` (incl. free-text `memo` seam locus)
      + deterministic seeded generator that can emit a FATF structuring/rapid-movement
      cluster — KS-0401 (`keystone.core.transactions`, `tests/test_transactions.py`;
      no detection/seam yet)
- [x] FATF typology engine: memo-BLIND detection (structuring / rapid-movement /
      large-transfer) over the stream → ledger findings; sample cluster caught,
      zero benign false positives — KS-0402 (`keystone.core.fatf`,
      `tests/test_fatf.py`)
- [x] **L2↔L1 seam milestone** — ONE transaction (TXN-000016) is both a FATF
      financial crime AND the memo-injection vuln; bound on a shared tx id against
      the single canonical signature; memo-blind AML proves independence — KS-0403
      (`keystone.assurance.seam`, `tests/test_seam.py`)
- [x] Regulator-format report generation: deterministic facts + FINnet/goAML adapters,
      guarded LLM narrative (faithfulness fall-back), draft→sign-off→ledger — KS-0404
      (`keystone.core.reporting`, `keystone.llm.report_narrative`, `tests/test_reporting.py`)
- [x] **Layer-1 milestone (NAT-orchestrated)** — ingest → FATF catches fraud →
      seam binds the same tx to the L2 signature (referenced, not re-run) → FINnet
      report → human sign-off → full hash-valid arc; `make layer1-milestone` runs it
      live — KS-0405 (`keystone.assurance.layer1_milestone`, `keystone.agents.orchestrator`,
      `tests/test_layer1_milestone.py`)

## Next — Phase 5 = Integration & demo (narrative-first redesign)

Two designed hero screens over a real run-result, framed by a supporting shell.

- [x] Demo runner + serializable run-result (the UI's typed contract over the
      Layer-1 arc) — KS-0500 (`keystone.demo`, `tests/test_demo_run_result.py`)
- [ ] Shared design system + the **seam hero** screen (one event, two failures) — KS-0501
- [ ] Jurisdiction-contrast hero (EU vs India) — KS-0502
- [ ] Supporting shell (ledger / posture / assurance before-after) — KS-0503
- [ ] Recorded-run fallback (offline replay) — KS-0504
- [ ] Demo script + rehearsal — KS-0505

(Re-phased from the old posture-dashboard / golden-path / offline-fallback trio;
the dashboard content survives as the KS-0503 supporting shell.)

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
