# DECISIONS.md — Architecture Decision Records

Lightweight ADRs. Newest at the bottom. Status: Accepted unless noted.
Linked from [`ARCHITECTURE.md`](ARCHITECTURE.md) and indexed in
[`docs/index.md`](docs/index.md).

**Format (every ADR):** `## ADR-NNNN — <title>`, then `**Status:**` · `**Date:**`,
then `**Context.**` / `**Decision.**` / `**Consequences.**` paragraphs.

| ADR | Title | Status |
| --- | --- | --- |
| 0001 | Pin Python to 3.12 (only) | Accepted |
| 0002 | Use `uv` for dependency management | Accepted |
| 0003 | Install `garak` as an isolated CLI subprocess | Accepted |
| 0004 | Run pre-commit (incl. detect-secrets) as a CI gate | Accepted |
| 0005 | Progressive-disclosure docs: thin `CLAUDE.md` + `docs/` tree | Accepted |
| 0006 | Machine-checkable feature list + validator | Accepted |

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

---

## ADR-0005 — Progressive-disclosure docs: thin `CLAUDE.md` + `docs/` tree

**Status:** Accepted · **Date:** 2026-06-15

**Context.** `CLAUDE.md` mixed map and doctrine (hard constraints + cross-cutting
principles inline), `docs/` was empty, and governance files were reachable only
by name, not by path. The harness philosophy wants the entry file to be a *map*
and depth to live in versioned, cross-linked docs.

**Decision.** Rewrite `CLAUDE.md` as a thin (~80-line) map: one-liner,
non-negotiables (pointers), where-to-look table, the three-way state split, agent
operating rules, and commands. Move depth into a structured `docs/` tree:
`index.md`, `design/` (`core-principles.md`, `architecture-boundaries.md`),
`exec-plans/{active,completed}/`, `references/`, `generated/`. Cross-link
everything; normalize ADRs with an index table and link them from
`ARCHITECTURE.md`. Document the three-way state split (`MEMORY.md` = durable
facts, `exec-plans/` = live state, agent memory store = runtime).

**Consequences.** Agents read a small map and follow pointers, keeping context
budget low. Some pointers (`feature_list.json`, `QUALITY.md`, `make verify`,
`.claude/commands/`) are forward references fulfilled in later phases this
session. Doc drift is a new risk → a freshness check is added in the continuity
phase.

---

## ADR-0006 — Machine-checkable feature list + validator

**Status:** Accepted · **Date:** 2026-06-15

**Context.** Scope lived only as prose in `ROADMAP.md`/`TASKS.md`, which cannot
be asserted against. Agents need a structured artifact with explicit
done-criteria and links to the tests that prove each item.

**Decision.** Add `docs/feature_list.json` as the source of truth: ~16 items at
medium granularity (ROADMAP phases decomposed one level into verifiable slices),
each with id, title, description, phase, status, `done_criteria`, and `tests`.
Items are derived **only** from existing roadmap scope. A typed validator
(`scripts/validate_feature_list.py`) enforces the schema and, critically, fails
if an item past `planned` has no tests or references a nonexistent test/node
(AST-collected). It runs in `pytest` (so the `check` gate covers it) and is
runnable standalone for `make verify`. `scripts/` is now linted/typed (added to
ruff, mypy `files`, and pytest `pythonpath`). `ROADMAP.md`/`TASKS.md` remain the
human-readable views and point at the JSON.

**Consequences.** "Done" is now mechanically checkable and tied to tests. New
work must add a feature entry with done-criteria before it can be marked beyond
`planned`. The validator is the place to harden future rules (e.g. requiring a
milestone test per phase).
