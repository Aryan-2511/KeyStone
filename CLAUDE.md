# CLAUDE.md — entry map for Keystone

> **Keystone** is a single-developer demo of an **orchestrated compliance &
> assurance** workflow on the NVIDIA agentic stack (NeMo Agent Toolkit +
> Guardrails, Garak for red-teaming) — deterministic by design where auditability
> demands it, and now a **multi-agent system** (two genuine agents — a Red-Team
> Agent + a Triage Agent, observation-driven policies, NOT LLMs; Movements A/B
> done). Deterministic core, LLM edge, synthetic data, hash-chained evidence ledger.

This file is a **map, not an encyclopedia**. Read the pointer for your task —
don't load the whole tree. Depth lives in [`docs/`](docs/index.md).

## Non-negotiables (full rationale → [core-principles](docs/design/core-principles.md))

- **Python 3.12 only** (`>=3.12,<3.13`). `ADR-0001`.
- **`uv` only** as package manager; commit `uv.lock`. `ADR-0002`.
- **`garak` is not a project dependency** — isolated CLI, called as a subprocess. `ADR-0003`.
- **Strict gates, never weakened.** mypy strict, Ruff security rules, coverage
  floor. Fix the code or ask — never relax a gate or add a blanket
  `# type: ignore` / `noqa`.
- **Synthetic data only.** No real data, no secrets, ever.
- **Out of scope:** Docker, tox, Sphinx, multi-version CI matrices.

## Where to look

| Your task | Start here |
| --- | --- |
| Orient / find any doc | [`docs/index.md`](docs/index.md) |
| Understand the principles | [`docs/design/core-principles.md`](docs/design/core-principles.md) |
| Architecture & layer boundaries | [`ARCHITECTURE.md`](ARCHITECTURE.md), [`docs/design/architecture-boundaries.md`](docs/design/architecture-boundaries.md) |
| Why a choice was made | [`DECISIONS.md`](DECISIONS.md) (ADRs) |
| What to build / done-criteria | `docs/feature_list.json` (source of truth), [`ROADMAP.md`](ROADMAP.md) / [`TASKS.md`](TASKS.md) (human view) |
| Acceptance / grading criteria | `docs/QUALITY.md` |
| Resume or hand off a task | [`docs/exec-plans/`](docs/exec-plans/) |
| Durable project facts | [`MEMORY.md`](MEMORY.md) |
| Changing deps / tooling | [`pyproject.toml`](pyproject.toml), [`DECISIONS.md`](DECISIONS.md) |

_(Italic paths are added in later phases; see [`ROADMAP.md`](ROADMAP.md).)_

## State: three separate stores (don't conflate)

1. **`MEMORY.md`** — durable, versioned facts true across all sessions.
2. **`docs/exec-plans/`** — live per-task state that survives context resets.
3. **Agent memory store** — runtime/ephemeral; not the system of record.
   Promote anything durable into 1 or 2.

## Operating rules for agents

1. **Audit before you build.** Understand the current state before changing it.
2. **Mechanical enforcement over prose.** Prefer a linter / structural test / CI
   check to a written rule.
3. **Generator/evaluator separation.** Verification is a separate, skeptical
   step — don't grade your own work leniently.
4. **Simplest thing that works.** Don't add a component unless it earns its
   place; mark premature ones as explicit *deferred*.
5. **Record decisions.** Every structural choice → an ADR in `DECISIONS.md`.
6. **Leave a clean handoff.** Update the exec-plan and run the verify gate before
   finishing.
7. **Don't invent scope.** Infer from code/docs and state the inference; list
   unknowns as open questions rather than filling them.

## Commands

| Command | What it does |
| --- | --- |
| `make setup` | Pin 3.12, `uv sync --all-groups`, install garak tool |
| `make check` | Gate: lint + typecheck + fast tests + audit (mirrors CI `check` job) |
| `make verify` | Skeptical, independent verification gate (see `docs/QUALITY.md`) |
| `make test` / `make test-all` | Fast tests / full suite |
| `make demo` | Console front door: run the real arc offline + narrate it (`uv run keystone demo`) |
| `make ui` | Launch the Streamlit visual app (`streamlit run src/keystone/ui/app.py`) |

CI runs three gates on every push/PR: **`pre-commit`** (detect-secrets +
hygiene), **`check`** (fast), and **`verify`** (full suite + scope validation).
All must be green.

**Loop commands** (in [`.claude/commands/`](.claude/commands/)):
[`/new-exec-plan`](.claude/commands/new-exec-plan.md) to start a task,
[`/verify`](.claude/commands/verify.md) to run the gate,
[`/finish-task`](.claude/commands/finish-task.md) to verify + hand off + archive.

## Directory map

```
src/keystone/   # application package (src-layout); py.typed shipped
tests/          # pytest suite; markers: slow, milestone
docs/           # knowledge base — start at docs/index.md
.claude/        # commands/ (agent loop ops) + settings
pyproject.toml  Makefile  .pre-commit-config.yaml  .github/workflows/ci.yml
```
