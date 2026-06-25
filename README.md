# Keystone

An **orchestrated compliance & assurance** demo built on the NVIDIA agentic
stack — [NeMo Agent Toolkit](https://github.com/NVIDIA/NeMo-Agent-Toolkit)
(`nvidia-nat`) for orchestration, [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
for policy, and [Garak](https://github.com/NVIDIA/garak) for red-teaming.
**Deterministic by design** where auditability demands it (FATF detection, the seam
binding, the hash-chained ledger) — that determinism is a feature, not a gap — and
**becoming a multi-agent system**: genuine offensive (Red-Team) and supervisory
(Triage) agents are being added where real reasoning and decisions live (Movements
A/B). Nothing today is claimed as a reasoning agent.

> **Status:** Phase 0 — tooling harness only. No application logic yet.

## Prerequisites

- **Python 3.12** (and only 3.12 — see `ADR-0001` in `DECISIONS.md`).
- **[`uv`](https://docs.astral.sh/uv/)** as the package manager.
- **A working C/C++ compiler.** NeMo Guardrails pulls in `annoy`, which builds a
  native extension from source. Without a toolchain `uv sync` will fail to build
  it.
  - **Linux:** `sudo apt-get install build-essential`
  - **macOS:** `xcode-select --install` (Xcode Command Line Tools)
  - **Windows:** "Desktop development with C++" workload from the Visual Studio
    Build Tools.

## Setup

```sh
uv python pin 3.12
uv sync --all-groups
uv tool install garak   # isolated CLI, NOT a project dependency
```

## Common commands

```sh
make check   # lint + typecheck + fast tests + audit (the gate; mirrors CI)
make test    # fast tests only
make demo    # run the demo (placeholder until a later phase)
```

See `CLAUDE.md` for the full directory map and standing rules.

## Data policy

**Synthetic data only.** No real customer data, no secrets, ever. The
`detect-secrets` pre-commit hook blocks committed credentials.
