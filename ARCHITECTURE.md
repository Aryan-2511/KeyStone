# ARCHITECTURE.md

> Phase 0 skeleton. Fill in as components land.

## One-line

Multi-agent compliance & assurance system: agents ingest synthetic artifacts,
apply policy via guardrails, and append verifiable findings to a hash-chained
evidence ledger.

## Layers

| Layer            | Responsibility                                         | Determinism |
| ---------------- | ------------------------------------------------------ | ----------- |
| Orchestration    | NeMo Agent Toolkit (`nvidia-nat`) workflow (YAML)      | config      |
| Policy / safety  | NeMo Guardrails (input/output/dialog rails)            | rules       |
| LLM edge         | Extraction, summarization, NL interaction              | LLM         |
| Deterministic core | Compliance logic, scoring, evidence ledger           | pure        |
| Red-team         | Garak (subprocess) probes the deployed surface         | external    |
| UI               | Streamlit demo front-end                               | n/a         |

## Key decisions (see DECISIONS.md)

- Python 3.12 only (`ADR-0001`).
- `uv` for dependency management (`ADR-0002`).
- garak isolated as a CLI subprocess (`ADR-0003`).

## Inference switch

A single config toggle selects the inference backend on one code path:

- **Hosted NIM** → demo mode (no local GPU needed).
- **Local Ollama** → production mode.

## Evidence ledger

Append-only, hash-chained records (each entry commits to the prior entry's
hash) backed by SQLite. Gives a tamper-evident audit trail. _To be designed._

## Data flow

_TODO: diagram once the NAT workflow skeleton exists (Phase 1)._
