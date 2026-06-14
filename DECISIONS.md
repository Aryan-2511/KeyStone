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

---

## ADR-0004 — Run pre-commit (incl. detect-secrets) as a first-class CI gate

**Status:** Accepted · **Date:** 2026-06-15

**Context.** The harness advertised detect-secrets + hygiene hooks as gates, but
they ran nowhere automatically: not in CI, and `pre-commit install` had never
been run. A committed secret would have passed CI. `make check` deliberately
does not include pre-commit (it mirrors the test/type/lint/audit gate).

**Decision.** Add a dedicated `pre-commit` job to `ci.yml` that runs
`uvx pre-commit run --all-files` on every push and PR. Keep it separate from the
`check` job so the secret/hygiene gate fails independently and visibly. Install
the local git hook (`pre-commit install`) for fast feedback.

**Consequences.** Secret scanning and hygiene are enforced on every PR, not by
convention. CI now has two gates: `pre-commit` and `check`.
