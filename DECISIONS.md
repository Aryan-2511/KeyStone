# DECISIONS.md — Architecture Decision Records

Lightweight ADRs. Newest at the bottom. Status: Accepted unless noted.

---

## ADR-0001 — Pin Python to 3.12 (only)

**Status:** Accepted · **Date:** 2026-06-14

**Context.** The stack must satisfy three tools simultaneously: NeMo Agent
Toolkit (`nvidia-nat`, `>=3.11,<3.14`), NeMo Guardrails (`nemoguardrails`), and
Garak (`garak`). The historically safe intersection that all three support is
**3.12**. 3.13+ has previously broken Garak/Guardrails; <3.12 is below floors we
want.

**Decision.** `requires-python = ">=3.12,<3.13"`. CI runs a single 3.12 job (no
matrix). `uv.lock` pins exact resolved versions.

**Consequences.** One known-good interpreter; no version-matrix friction. Must
re-validate the intersection before any future bump.

---

## ADR-0002 — Use `uv` for dependency management

**Status:** Accepted · **Date:** 2026-06-14

**Context.** Need fast, reproducible, lockfile-based resolution with PEP 735
dependency groups.

**Decision.** `uv` is the only package manager. `uv sync`, `uv add`, `uv run`,
`uv tool`. Never pip/poetry/conda. `uv.lock` is committed.

**Consequences.** Reproducible installs; single tool for envs, runs, and tools.
Contributors must install uv.

---

## ADR-0003 — Install `garak` as an isolated CLI subprocess (not a dependency)

**Status:** Accepted · **Date:** 2026-06-14

**Context.** Garak's transitive dependency closure is large and can conflict
with the NAT + Guardrails resolution. We only invoke garak as an external
red-team driver, not as a library.

**Decision.** Install via `uv tool install garak` (isolated environment). Call
it as a subprocess. It is **not** listed in `pyproject.toml` dependencies.

**Consequences.** No transitive-dep contamination of the core resolution.
Garak's version is managed separately from `uv.lock`.
