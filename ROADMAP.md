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

## Phase 2 — Agents & policy

- Compliance/assurance agents on the NAT workflow.
- NeMo Guardrails rails (input/output/dialog).

## Phase 3 — Assurance & red-team

- Garak probes wired as a subprocess against the deployed surface.
- Milestone tests (`-m milestone`) proving the end-to-end assurance loop.

## Phase 4 — Demo UI

- Streamlit front-end over the workflow and ledger.

_Out of scope throughout: Docker, tox, Sphinx, multi-version CI._
