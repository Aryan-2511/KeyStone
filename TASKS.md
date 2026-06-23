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
- [x] Shared design system + the **seam hero** screen (one event, two failures) — KS-0501
      (`keystone.ui.tokens`, `.streamlit/config.toml`, `keystone.ui.seam_screen`,
      `keystone.ui.seam_app`; `tests/test_ui_tokens.py`, `tests/test_seam_screen.py`)
- [x] Jurisdiction-contrast hero (EU vs India) — KS-0502
      (`keystone.ui.svg` shared primitives, `keystone.ui.jurisdiction_screen`,
      `keystone.ui.jurisdiction_app`; RunResult schema v2 = + goAML + EU/India
      modality; `tests/test_jurisdiction_screen.py`, `tests/test_jurisdiction_app.py`)
- [x] Supporting shell (ledger / posture / assurance before-after) — KS-0503
      (`keystone.ui.shell_app` hosts both heroes + 3 views via `keystone.ui.shell_screens`;
      RunResult schema v3 = + referenced assurance before/after (`keystone.assurance.REFERENCED_ASSURANCE`);
      `tests/test_shell_screens.py`, `tests/test_shell_app.py`)
- [x] Recorded-run fallback (offline replay) — KS-0504
      (`src/keystone/demo/recorded_run.json` via `keystone.demo.recorded_run_path`;
      the shell's safe default; proven offline in `tests/test_offline_fallback.py`)
- [ ] Demo script + rehearsal — KS-0505

(Re-phased from the old posture-dashboard / golden-path / offline-fallback trio;
the dashboard content survives as the KS-0503 supporting shell.)

## Movement 1 — the Seam Matrix (Phase 6; design contract `M1-00_SEAM_MATRIX_DESIGN.md`)

> Generalise the single TXN-000016 seam into a *characterized class*: a uniform
> framework binding (OWASP attack × FATF typology) pairs under one independence
> guarantee + one build-failing drift assertion. Build the framework first, then
> the pairs, then the result (same dependency discipline as the core build).

- [x] **Seam Framework abstraction** — bind any (attack, crime) pair uniformly;
      P1 re-expressed as the first instance through it (all existing seam tests
      pass unchanged = faithfulness proof). Independence enforced framework-level
      (the detector only ever sees a `FinancialProjection`, never the attack
      channel); CLEAN / BOUNDARY / OPEN are first-class results. — M1-01 / KS-0601
      (`keystone.assurance.framework`, `.pairs`; `tests/test_seam_framework.py`)
- [x] **P2 — Prompt Injection × Rapid-movement/layering** — binds CLEAN through the
      UNCHANGED framework; its rapid-movement cluster (small fast fan-out, sub-band)
      fires `RAPID_MOVEMENT` and NOT `STRUCTURING`, detector-distinct from P1. — M1-02 /
      KS-0602 (`keystone.assurance.seam_p2`, `core.transactions.rapid_sample_stream`;
      `tests/test_seam_p2.py`)
- [x] **P3 — Prompt Injection × Large-transfer/threshold** — binds CLEAN through the
      UNCHANGED framework; a single ≥$10k transfer fires `LARGE_TRANSFER` and NEITHER
      other typology (the cleanly-exclusive pair). Completes Axis A (one attack class →
      three distinct typologies). — M1-03 / KS-0603 (`keystone.assurance.seam_p3`,
      `core.transactions.large_sample_stream`; `tests/test_seam_p3.py`)
- [x] **P4 — Sensitive Information Disclosure × (none) — THE BOUNDARY** — a PROVEN
      NEGATIVE through the framework's `BOUNDARY` result: an exfil attack that moves no
      money → zero typologies fire → the seam provably does NOT bind. Principled (a
      property of the attack, not a missing detector) and build-protected. — M1-04 /
      KS-0604 (`keystone.assurance.seam_p4`; `tests/test_seam_p4.py`)
- [x] **P5 — Excessive Agency / tool-misuse × unauthorized-recipient** — Axis B (beyond
      injection, OWASP LLM08). Built via PATH A: a NEW minimal, INDEPENDENT recipient
      screen (standing flagged-destination list in `core.fatf`) — the only new detector
      in M1. Binds CLEAN as-found (honest caveat: the tool-call channel is synthetically
      represented). — M1-05 / KS-0605 (`core.fatf.FLAGGED_DESTINATIONS`,
      `keystone.assurance.seam_p5`; `tests/test_seam_p5.py`)
- [x] **The characterized-mapping result** — the matrix as a RESULT: a `matrix` block on
      the RunResult (schema v4, derived from `REGISTERED_PAIRS`) + the third hero
      (convergence figure: five attacks → one framework → results; P4 a deliberate
      dashed boundary). Hosted in the shell; AppTest-gated; caveats reachable off the
      hero. — M1-06 / KS-0606 (`keystone.demo.matrix`, `keystone.ui.matrix_screen` /
      `matrix_app`; `tests/test_matrix_screen.py`, `tests/test_matrix_app.py`;
      screenshot `docs/assets/m1-06-matrix-hero.png`)

> **MOVEMENT 1 IS COMPLETE.** Final as-found distribution: **4 CLEAN** (P1 structuring,
> P2 rapid-movement, P3 large-transfer, P5 unauthorized-recipient) **+ 1 BOUNDARY** (P4
> exfil). Two axes sampled: Axis A (one attack class → three typologies, P1-P3) and Axis
> B (beyond injection — P4 boundary at LLM06, P5 clean at LLM08). The characterized
> mapping + its boundary is surfaced as the M1-06 result/figure.

> Step-0 recon (locked in `M1-00` §7a): the FATF engine already has **distinct**
> structuring / rapid-movement / large-transfer detectors (P2/P3 are separable,
> no collapse risk). It has **no** recipient/sanctions typology, so P5 likely
> takes the §6 fallback (a clean fourth injection pair) — decided at M1-05 start.

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
