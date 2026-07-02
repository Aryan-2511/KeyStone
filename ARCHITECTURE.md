# ARCHITECTURE.md

> The three compliance layers, the seam matrix, the convergence result, and both
> agents are built. This file describes the system as it stands.
>
> Related: [`DECISIONS.md`](DECISIONS.md) (ADR log) ·
> [`docs/design/core-principles.md`](docs/design/core-principles.md) (the *why*) ·
> [`docs/design/architecture-boundaries.md`](docs/design/architecture-boundaries.md)
> (the enforced dependency contract).

## One-line

An orchestrated compliance & assurance system: a NeMo Agent Toolkit workflow
sequences deterministic stages that ingest synthetic artifacts, apply policy via
guardrails, and append verifiable findings to a hash-chained evidence ledger.
Deterministic by design where auditability demands it (FATF detection, the seam,
the ledger) — a feature, not a gap. It is now a **multi-agent system**: two genuine
agents in a supervisor–worker topology — a Red-Team Agent (offensive worker) and a
Triage Agent (supervisor) — each an observation-driven policy that clears a strict
agency bar (the next action depends on what it observed), NOT an LLM. Option A
(LLM-reasoned selection) is a named later upgrade.

## Layers

| Layer            | Responsibility                                         | Determinism |
| ---------------- | ------------------------------------------------------ | ----------- |
| Orchestration    | NeMo Agent Toolkit (`nvidia-nat`) workflow (YAML)      | config      |
| Policy / safety  | NeMo Guardrails (input/output/dialog rails)            | rules       |
| LLM edge         | Extraction, summarization, NL interaction              | LLM         |
| Deterministic core | Compliance logic, scoring, evidence ledger           | pure        |
| Red-team         | Garak (subprocess) probes the deployed surface         | external    |
| Agents           | Red-Team Agent (offensive) + Triage Agent (supervisor) — observation-driven policies | policy |
| UI               | Streamlit demo front-end                               | n/a         |

## Key decisions (see [`DECISIONS.md`](DECISIONS.md))

- Python 3.12 only — [`ADR-0001`](DECISIONS.md#adr-0001--pin-python-to-312-only).
- `uv` for dependency management — [`ADR-0002`](DECISIONS.md#adr-0002--use-uv-for-dependency-management).
- garak isolated as a CLI subprocess — [`ADR-0003`](DECISIONS.md#adr-0003--install-garak-as-an-isolated-cli-subprocess-not-a-dependency).
- pre-commit as a CI gate — [`ADR-0004`](DECISIONS.md#adr-0004--run-pre-commit-incl-detect-secrets-as-a-first-class-ci-gate).

The deterministic-core → edge dependency direction (LLM edge must not be
imported by the core) is enforced mechanically; see
[`docs/design/architecture-boundaries.md`](docs/design/architecture-boundaries.md).

## Inference switch

A single config toggle selects the inference backend on one code path:

- **Hosted NIM** → demo mode (no local GPU needed).
- **Local Ollama** → production mode.

## Evidence ledger

Append-only, hash-chained records (each entry commits to the prior entry's
hash) backed by SQLite — a tamper-evident audit trail. Implemented in
`keystone.core.ledger` (KS-0102/0103).

## Data flow

Synthetic artifacts → deterministic detection (FATF) → the seam binds detection to
reporting across a memo-blind boundary → obligation/control mapping → the Red-Team
Agent probes the guarded surface and the Triage Agent routes findings → every step
appends to the hash-chained ledger. The convergence view shows a seam event taking
named obligations from *violated* to *satisfied*. Rendered in the Streamlit app
(`make demo`).
