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
| 0010 | Chassis layout + NAT untyped-boundary mypy relaxation | Accepted |
| 0011 | Realign phases 2–5 to the three compliance layers | Accepted |
| 0012 | Obligation data model and storage (KS-0201) | Accepted |
| 0013 | Override transitive cryptography<47 cap to clear GHSA-537c-gmf6-5ccf | Accepted |

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

---

## ADR-0010 — Chassis layout + NAT untyped-boundary mypy relaxation

**Status:** Accepted · **Date:** 2026-06-15

**Context.** The Phase-1 chassis (ledger, inference switch, NAT orchestrator,
Streamlit shell) had to land somewhere. Phase 4 already created enforced layer
packages (`keystone.core`, `keystone.llm`, `keystone.agents`, `keystone.ui`).
Separately, `nvidia-nat` ships **no `py.typed`**, which collides with mypy
strict.

**Decision.**
- **Layout (per user choice):** nest the chassis under the layer packages —
  ledger=`keystone.core.ledger`, inference=`keystone.llm.inference`,
  orchestrator=`keystone.agents.orchestrator`, shell=`keystone.ui.app`, run
  entrypoint=`keystone.agents.run`. This reuses the enforced architecture; the
  existing import-linter contract already forbids the core (ledger) from
  importing the edge. The literal task command `python -m keystone.orchestrator`
  becomes `python -m keystone.agents.run`; `make demo` runs the UI module.
- **NAT untyped boundary:** rather than scatter `# type: ignore`, relax exactly
  two strict sub-flags (`disallow_subclassing_any`, `disallow_untyped_decorators`)
  for ONLY `keystone.agents.orchestrator.*`, plus a `call-arg` waiver on
  `…orchestrator.config` (the `name=` class kwarg). Everything else stays fully
  strict; no inline ignores anywhere.

**Consequences.** The chassis is architecturally coherent and the boundary
contract covers it for free. The NAT relaxation is confined to the one
integration module and documented; `keystone.core`/`llm`/`ui` and all tests
remain under unmodified strict. The Streamlit shell is omitted from coverage
(UI glue verified by `make demo`). NAT API quirks recorded in `MEMORY.md`.

---

## ADR-0011 — Realign phases 2–5 to the three compliance layers

**Status:** Accepted · **Date:** 2026-06-16

**Context.** `ROADMAP.md` and `docs/feature_list.json` carried a generic
"agents & policy / assurance & red-team / demo UI" decomposition that had dropped
the **three compliance layers that are the product**. Phase numbers (engineering
build order) and layer names (product meaning) had drifted into two inconsistent
axes, and the L2↔L1 seam — the planted fraudulent transfer entering via the same
indirect-prompt-injection path Garak exercises — was implicit rather than owned.

**Decision.** Make build order and layer naming **one axis**: each phase names the
layer it delivers. Phases 0 (Harness) and 1 (Chassis) are DONE and unchanged.
Realign:
- **Phase 2 — Layer 3: Obligation Mapper** (deterministic-heavy). Re-scope the old
  generic "compliance agent" (KS-0201) into a curated, source-cited obligation
  graph + deterministic crosswalk/dedup + an explicit EU-vs-India modality
  contrast + LLM-edge-only summary phrasing + a citation-validation accuracy
  budget (KS-0201–0205).
- **Phase 3 — Layer 2: AI Assurance Loop**: mock vulnerable agent + Guardrails
  (old KS-0202) + Garak (old KS-0301) + assurance-loop milestone (old KS-0302),
  renumbered to KS-0301–0304.
- **Phase 4 — Layer 1: Transaction Monitor + the L2↔L1 seam** (KS-0401–0403). The
  seam is **one owned item** (KS-0403): a `@pytest.mark.milestone` test asserting
  the fraud fixture's injection vector == the Garak-flagged vector, structurally,
  so a refactor that decouples them fails the build.
- **Phase 5 — Integration & demo**: posture dashboard (old KS-0401), golden path,
  offline fallback (KS-0501–0503).

IDs follow `KS-0Pnn` (P = phase), so any item that changed phase was renumbered;
items keep `id, title, phase, layer, status, done_criteria`. A `layer` field was
added to every feature (Harness/Chassis for the done infra phases); no DONE
item's id, phase, or status changed. `version` bumped to 2. `ROADMAP.md`,
`TASKS.md`, and `feature_list.json` now describe the same phases, numbers, layer
names, and IDs.

**Consequences.** The roadmap reads as the product (three layers) instead of a
generic agent pipeline; the L2↔L1 seam is a first-class, mechanically-asserted
deliverable rather than an emergent coincidence; and the accuracy budget for
obligation citations is an explicit gate. Phase 2 is now the Obligation Mapper.
No application code, tests, or exec-plans were changed by this realignment.

---

## ADR-0012 — Obligation data model and storage

**Status:** Accepted · **Date:** 2026-06-16

**Context.** KS-0201 (Phase 2 / Layer 3 — Obligation Mapper) needs a curated
graph of ~25–30 regulatory obligations, each carrying a verifiable source
citation. The model + storage shape is referenced forward by KS-0202 (control
crosswalk/dedup), KS-0203 (modality contrast), KS-0204 (LLM-edge summary
phrasing), and KS-0205 (the build-failing citation-validation gate). Locking the
schema once, before any curation or code, keeps those four items consistent and
lets KS-0205 be implemented as "validate the data file against this schema."
This module is deterministic core and is bound by ADR-0008 (the core must not
import the LLM edge) and by QUALITY.md rows #3 (scope/done_criteria), #6
(architecture boundary), and #8 (synthetic/no-secrets; here: cite public legal
instruments accurately).

**Decision.**

1. **Storage = a data file loaded through a typed Pydantic model.** Obligations
   are *content*, not logic, so curated nodes live in a data file shipped in the
   package data dir (`src/keystone/core/obligations/data/obligations.json`),
   loaded and validated via a Pydantic v2 model — mirroring how
   `keystone.core.ledger` models its records and how `workflow.yml` ships as
   package data (`Path(__file__).parent / ...`). Rationale: content is reviewable
   without reading code; KS-0205's gate reduces to schema-validating the file
   (mirroring `scripts/validate_feature_list.py`); Phase 4 adds jurisdictions as
   *data*, not forked code.

2. **The loader fails loudly — binding invariant.** A malformed node, an unknown
   enum value, a duplicate `id`, or a node missing a required citation field is a
   **hard load error**. Obligations are never skipped, never defaulted, never
   partially loaded. A silently-dropped obligation is precisely the coverage gap
   this product exists to detect, so degrading gracefully is a defect, not a
   convenience. (Pydantic strict validation + an explicit duplicate-`id` check.)

3. **Citation is a structured object, not a free-text string.** This lets KS-0205
   validate mechanically (e.g. all five instruments represented; `provision`
   matches a per-instrument pattern; `retrieved` is a real date). Free text
   cannot be gated.

4. **Deterministic-core boundary.** Model, data file, and loader live under
   `keystone.core.obligations`; import-linter (ADR-0008) forbids any
   `agents/policy/llm/ui/assurance` import. The `summary` field is the **curated,
   human-written** source description and is the system of record. KS-0204's LLM
   phrasing is a SEPARATE, later, edge-side transform that *reads* `summary` and
   produces a derived presentation string elsewhere — it must never write back
   into this core data, and no LLM code may be imported here.

5. **Control-library representation = Option A (chosen).** The control library is
   its own data file (KS-0202's deliverable); obligations reference controls by
   `control_id` via `control_ids: list[str]`. Rationale: the control is the
   independently-existing entity that obligations attach to, so the "N obligations
   → M controls" crosswalk is read directly from the data rather than derived —
   that crosswalk is the Layer 3 headline, the file is the single source of truth
   for control text, and it is the shared spine Phase 4's pluggable jurisdictions
   point at. Two binding conditions make A safe, not merely chosen:

   - **(5a) `control_ids` is optional / may be empty in KS-0201.** Authoring the
     control library is KS-0202's job. KS-0201 curates obligations whose
     `control_ids` may be empty; it does NOT author controls and does NOT depend
     on the library existing. Option A only *reserves* the reference shape now —
     it does not couple the two tasks.
   - **(5b) KS-0202 must ship a fail-loud referential-integrity validator.** Once
     the control library exists, every non-empty `control_id` on any obligation
     MUST resolve to a real control in the library; an unresolved reference is a
     hard error — never skipped, never defaulted — the same fail-loud invariant as
     the loader (decision 2). This is recorded here as a **KS-0202 acceptance
     criterion**, and `feature_list.json` KS-0202 must carry it as a
     `done_criterion` when KS-0202 is moved past `planned`.

**Schema (locked).**

```
Obligation:
  id: str                        # stable identifier, e.g. "OBL-EUAI-012".
                                 #   Unique; referenced by other phases. Pattern: ^OBL-[A-Z0-9]+-\d{3}$
  instrument: Instrument         # enum (see below)
  citation: Citation             # structured object (see below)
  summary: str                   # curated human-written source text (NOT LLM-phrased); non-empty
  enforcement_modality: Modality # enum; feeds KS-0203
  jurisdiction: Jurisdiction     # enum; feeds Phase 4
  control_ids: list[str]         # forward ref to KS-0202 control library; OPTIONAL, default []
                                 #   (see decision 5a/5b)

Citation:
  instrument: Instrument         # required; MUST equal the parent Obligation.instrument (validated)
  provision: str                 # required; the article/section, e.g. "Art. 9" / "s. 8(5)".
                                 #   KS-0205 checks it against a per-instrument pattern
  title: str                     # required; human-readable provision title
  url: str | None                # optional; canonical source link
  retrieved: datetime.date | None # optional; ISO date (YYYY-MM-DD) the citation was last verified
```

**Enums (full member sets).**

- `Instrument`: `EU_AI_ACT` | `DORA` | `DPDP_ACT` | `DPDP_RULES_2025` |
  `RBI_GUIDANCE` | `PMLA_FIU_IND`
- `Modality`: `HARD_LAW` | `SELF_CERTIFICATION`
- `Jurisdiction`: `EU` | `INDIA`

**Field rules.**

- **Required:** `id`, `instrument`, `citation`, `summary`, `enforcement_modality`,
  `jurisdiction`. `control_ids` defaults to `[]` (decision 5a).
- **Citation required:** `instrument`, `provision`, `title`. **Optional:** `url`,
  `retrieved`.
- `retrieved` is an **ISO date** so the accuracy budget can surface staleness —
  KS-0205 can flag citations older than a threshold or missing a `retrieved` date,
  making stale references visible rather than silently trusted.
- `id` and `control_ids` are **stable identifiers** other phases reference; renaming
  an `id` is a breaking change. `citation.instrument` must equal the obligation's
  `instrument` (a cross-field validator), so the citation can't drift from its node.

**Consequences.** The four downstream items build on a fixed shape: KS-0205
validates the file against this schema and the per-instrument provision patterns;
KS-0203 reads `enforcement_modality`; KS-0202 authors the control library and adds
the referential-integrity check (5b) over `control_ids`; KS-0204 derives
presentation text from `summary` at the edge. The fail-loud invariants (decisions 2
and 5b) mean curation and mapping errors block the build instead of shrinking
coverage silently. Option A costs a second data file and an authoring order
(controls before references resolve), but condition 5a keeps KS-0201 independent of
that ordering. JSON is chosen over YAML for the data file: consistency with
`docs/feature_list.json` (so KS-0205 mirrors `scripts/validate_feature_list.py`)
and avoidance of YAML type-coercion footguns in a citation file where
`provision`/codes must stay literal text.

## ADR-0013 — Override the transitive cryptography<47 cap to clear GHSA-537c-gmf6-5ccf

**Status:** Accepted · **Date:** 2026-06-17

**Context.** `make verify`'s `pip-audit` gate flags transitive `cryptography`
46.0.7 (GHSA-537c-gmf6-5ccf; OSV range introduced 0.5.0, **fixed only in
48.0.1** — no patched line below 48). `cryptography` is pulled in by
`nvidia-nat-core`, `authlib`, and `joserfc`; `authlib`/`joserfc` accept ≥48, but
**`nvidia-nat-core` 1.7.0 declares `cryptography<47,>=46.0.6`**, which strands us
on the vulnerable line. This is pre-existing on `main` (no project dependency
introduced it). A strict gate must not be silenced (CLAUDE.md), so the fix has to
remove the actual vulnerable package, not the finding.

**Investigation (live PyPI metadata, not assumed versions).**

1. **No `nvidia-nat` bump helps.** Latest *stable* `nvidia-nat`/`nat-core` is
   **1.7.0** (our pin); everything newer is a prerelease (1.8.0rcN, 1.9.0aN). The
   `cryptography<47,>=46.0.6` cap is present at 1.7.0 **and** through the newest
   prereleases. The only cap-free version is the older 1.6.0 (a downgrade), and no
   patched cryptography exists below 48 regardless.
2. **The cap is conservative, not a real incompatibility.** Forcing
   `cryptography>=48.0.1` (resolves to 49.0.0) and running the **full** gate —
   incl. the chassis milestone `test_chassis_runs_three_layers_and_chain_verifies`
   that exercises the NAT workflow API — passes, and `pip-audit` reports no
   vulnerabilities.

**Decision.** Add a uv override in `pyproject.toml`:
`[tool.uv] override-dependencies = ["cryptography>=48.0.1"]`. This raises the
resolved `cryptography` above `nat-core`'s declared upper bound while keeping the
NVIDIA stack on its stable 1.7.0 line. It is a security override, not a gate
relaxation: the `pip-audit` gate stays strict and now passes because the
vulnerable package is gone.

**Removal trigger.** Drop the override once a stable `nvidia-nat` ships a
`nat-core` whose declared `cryptography` constraint allows ≥48 (re-check the
`nat-core` `requires_dist` on a future bump). Tracked in
`docs/exec-plans/completed/dependency-hygiene-cryptography.md`.

**Consequences.** We assume responsibility for an out-of-declared-range
`cryptography` for `nat-core`; the risk is bounded because the full gate
(including the NAT-exercising milestone) is green on 49.0.0, and the override is
narrowly scoped to one package with a floor (`>=48.0.1`) rather than a pin, so
routine patch upgrades still flow. If a future `nat-core` genuinely needs
`cryptography<47` at runtime, the milestone test is the tripwire.
