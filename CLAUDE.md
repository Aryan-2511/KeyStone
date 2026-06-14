# CLAUDE.md — standing rules for Keystone

Read this first. It is the context anchor for every task in this repo.

## Hard constraints (do not deviate; ask if blocked)

- **Python 3.12 only.** `requires-python = ">=3.12,<3.13"`. Verified intersection
  of nvidia-nat (`>=3.11,<3.14`), nemoguardrails, and garak. Never 3.13+, never
  <3.12. See `ADR-0001`.
- **`uv` is the package manager.** Use `uv sync`, `uv add`, `uv run`, `uv tool`.
  Never pip/poetry/conda. Commit `uv.lock`. See `ADR-0002`.
- **`garak` is NOT a project dependency.** It is installed as an isolated CLI
  (`uv tool install garak`) and called as a subprocess. See `ADR-0003`.
- **Strict gates, never weakened.** mypy `strict = true`; Ruff with security
  rules (`S`); pytest `--cov-fail-under=70`. Fix the code or ask — never relax a
  gate, never add a blanket `# type: ignore` / `noqa` to go green.
- **Synthetic data only.** No real data, no secrets, ever. The detect-secrets
  hook must block credentials.
- **Out of scope:** Docker, tox, Sphinx, multi-version CI matrices.

## Commands

| Command         | What it does                                            |
| --------------- | ------------------------------------------------------- |
| `make setup`    | Pin 3.12, `uv sync --all-groups`, install garak tool    |
| `make check`    | The gate: lint + typecheck + fast tests + audit (= CI)  |
| `make test`     | Fast tests (`-m "not slow"`)                            |
| `make test-all` | Full suite incl. slow                                   |
| `make demo`     | Run the demo (placeholder in Phase 0)                   |

## Directory map

```
src/keystone/      # application package (src-layout); py.typed shipped
tests/             # pytest suite; markers: slow, milestone
docs/              # design notes
pyproject.toml     # deps, dependency-groups, Ruff/mypy/pytest config
Makefile           # task runner (check mirrors CI)
.pre-commit-config.yaml
.github/workflows/ci.yml
```

## Which files to read for which task (context budget)

- **Changing deps / tooling:** `pyproject.toml`, `DECISIONS.md`.
- **Architecture / data flow:** `ARCHITECTURE.md`.
- **What to build next:** `ROADMAP.md`, `TASKS.md`.
- **Why a choice was made:** `DECISIONS.md` (ADRs).
- **Durable project facts:** `MEMORY.md`.

Don't read the whole tree for a scoped task — start from the file above.

## Cross-cutting principles

- **Deterministic core / LLM edge.** Business logic, the evidence ledger, and
  policy decisions are deterministic and testable. LLMs live only at the edges
  (extraction, summarization, NL interaction).
- **Synthetic data only.** Fixtures and examples never use real data.
- **Inference is a config switch.** Hosted NIM = demo mode; local Ollama =
  production mode. Same code path, different config.
- **Hash-chained evidence ledger.** Every assurance event is appended to a
  tamper-evident, hash-chained ledger so the audit trail is verifiable.
