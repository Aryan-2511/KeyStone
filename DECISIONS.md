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
| 0007 | Verification loop: `make verify` + e2e + QUALITY.md | Accepted |
| 0008 | Enforce deterministic-core import boundary (import-linter) | Accepted |
| 0009 | Continuity + entropy control: exec-plans, commands, freshness | Accepted |

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

---

## ADR-0007 — Verification loop: `make verify`, e2e layer, QUALITY.md

**Status:** Accepted · **Date:** 2026-06-15

**Context.** The only gate was `make check` (fast inner loop). The harness
philosophy wants a *separate, skeptical* evaluator step, real end-to-end
assertions on actual surfaces, and acceptance criteria that don't reduce to a
coverage percentage.

**Decision.**
- Add `make verify` and a dedicated CI `verify` job: an independent acceptance
  gate that runs the scope validator standalone plus the **full** test suite
  (incl. `slow`/`milestone`/`e2e`) with the blocking coverage floor. Kept
  separate from `check` so verification isn't entangled with the inner loop.
- Seed `tests/e2e/` with a subprocess test of the **installed `keystone`
  console script** (per the e2e policy: exercise the real entry point, not
  `import main`). Breadth deferred. Add an `e2e` marker; scope a per-file ruff
  ignore for `S603` (subprocess) to `tests/e2e/**`, mirroring the existing
  `S101` precedent — spawning the built artifact is the point, not a finding.
- Add `docs/QUALITY.md`: the evaluator's rubric, with an explicit banner that
  **coverage is a floor, not a grade**, and guidance demanding adversarial tests
  for critical code (ledger tamper-detection, inference switch, guardrails).

**Consequences.** Two complementary CI gates (`check` fast, `verify` thorough).
The validator was confirmed to fail loudly on duplicate ids, done-without-tests,
and missing test refs. Acceptance is now defined in writing and partly
mechanical; `make verify` grows as enforcement (e.g. the import contract) lands.

---

## ADR-0008 — Enforce the deterministic-core import boundary with import-linter

**Status:** Accepted · **Date:** 2026-06-15

**Context.** `ARCHITECTURE.md` describes a deterministic core / LLM edge split,
but prose drifts from code. The decision (Q2) was to activate enforcement now,
minimally, rather than defer it — materializing only the layers ARCHITECTURE
already names.

**Decision.** Materialize the named layers as empty packages under
`src/keystone/` (`core`, `llm`, `policy`, `agents`, `assurance`, `ui`). Add
`import-linter` (dev group) with a thin `forbidden` contract: `keystone.core`
may not import `agents`/`policy`/`llm`/`ui`/`assurance`. The contract name
doubles as the remediation message. Enforce it in four places: `make
arch`/`check`/`verify`, a `local` pre-commit hook, the CI `check` job, and
`tests/test_architecture.py` (which runs the `lint-imports` CLI as a subprocess —
the canonical interface; the programmatic API needs undocumented init and trips
mypy's no-untyped-call, so the CLI is both simpler and more faithful). Scope an
`S603` per-file ignore to that test, mirroring the e2e precedent.

**Consequences.** A forbidden import now fails the build with the offending
chain. Confirmed non-vacuous: injecting `keystone.core -> keystone.llm` is
reported BROKEN. Grow the contract (e.g. layered ordering among edge packages)
as real modules land. import-linter is typed, so it is not in the mypy
`ignore_missing_imports` list.

---

## ADR-0009 — Continuity + entropy control: exec-plans, commands, freshness

**Status:** Accepted · **Date:** 2026-06-15

**Context.** Sessions lose state across context resets, and governance docs rot
when they silently diverge from reality. The harness needs a structured handoff
and a drift guard — and the loop should be *operable*, not just documented.

**Decision.**
- **Exec-plan handoff:** `docs/exec-plans/TEMPLATE.md` carries goal/acceptance,
  context, plan, progress log, decisions, blockers, next-steps, and a handoff
  section. Plans live in `active/` then move to `completed/` on finish.
- **Three-way state split** made explicit (`MEMORY.md` durable facts /
  `exec-plans/` live state / agent memory store runtime) in `MEMORY.md`,
  `CLAUDE.md`, and `docs/index.md`.
- **Operable loop:** `.claude/commands/` ships `/new-exec-plan`, `/verify`, and
  `/finish-task` so the loop ops are runnable, with a cleanup checklist baked
  into `/finish-task` (entropy control).
- **Freshness checks** (in `tests/test_docs.py`, so they gate in CI): ADR index
  table must match the actual ADR sections; the exec-plan template must exist —
  on top of the existing thin-CLAUDE.md / no-broken-links / governance-link
  checks.
- **Observability explicitly deferred** with a documented slot
  (`docs/design/observability.md`).

**Consequences.** Any session can resume from an exec-plan; doc drift fails the
build instead of rotting silently; the golden principles in
`core-principles.md` plus the cleanup checklist guard against entropy. Adding an
ADR now requires updating the index (enforced).
