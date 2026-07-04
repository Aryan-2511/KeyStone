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
| 0014 | The Seam Framework: independence as a typed framework property | Accepted |
| 0015 | Honestly multi-agent now — two probes, the §2 bar | Accepted |
| 0016 | The memo-blind boundary is sacred (independence → convergence) | Accepted |
| 0017 | Option B (policy) ships before Option A (LLM) | Accepted |
| 0018 | Determinism-by-design is a feature, not a gap | Accepted |
| 0019 | "remediate" is a route, not fix-selection (Movement C gate) | Accepted |
| 0020 | Deck leads problem-first + the buyer-split | Accepted |
| 0021 | Live Triage Agent: LLM opt-in, fallback is the safety architecture, honest by tag | Accepted |
| 0022 | Live Red-Team Agent: real Garak opt-in, recorded-profile fallback, source-tagged; LLM-selection compute-gated | Accepted |
| 0023 | Recorded defense profile refreshed to real OPT-A-02 captures (fixes promptinject drift) | Accepted |
| 0024 | Data-residency, not "offline": the load-bearing requirement is no-exfiltration | Accepted |
| 0025 | The two hardware findings + fine-tuning frontier = the evidence-backed on-prem compute ask | Accepted |
| 0026 | Triage LLM prompt-rescue: OPT-A-01's poor routing was part prompt, but a held-out probe confirms the model ceiling | Accepted |

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

**Amendment (2026-06-19) — KS-0300 inserted as a Phase-3 prerequisite.** The
Ollama-vs-NIM tool-calling spike found that plain `complete()` cannot tool-call,
so a tool-calling inference seam must exist *before* the mock agent (KS-0301) can
be built. Rather than renumber the already-settled KS-0301–0304, the seam is
recorded as **KS-0300** — a sub-0301 Phase-3 infrastructure item that, by number,
precedes the block. The prerequisite is made structural, not implied: KS-0301
carries `depends_on: ["KS-0300"]`, and `validate_feature_list.py` now enforces
that `depends_on` ids resolve. This is the one place a 0300 appears after
0301–0304 were numbered, and this note records why.

**Amendment (2026-06-20) — KS-0303 (Garak) built before KS-0302 (Guardrails).**
ADR-0011 numbered Guardrails (KS-0302) before the Garak red-team (KS-0303), but
they are built in the reverse order: the *detector* that finds the mock agent's
memo-injection flaw must exist **before** the *patch* (Guardrails) it will verify —
you can't prove a rail closed a hole you can't yet detect. The numbers are NOT
changed (KS-0302 stays Guardrails, KS-0303 stays Garak); only the build order is
inverted. To make the dependency structural, KS-0302 now carries
`depends_on: ["KS-0303"]` (the rail's done-criteria — Garak finds fewer/zero hits
after the rail — needs the KS-0303 detector). KS-0303 itself consumes the KS-0301
agent's canonical `MEMO_INJECTION_SIGNATURE`, so it `depends_on` KS-0301.

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

## ADR-0014 — The Seam Framework: independence as a typed framework property

**Status:** Accepted · **Date:** 2026-06-23

**Context.** Movement 1 (`M1-00_SEAM_MATRIX_DESIGN.md`) generalises the single
`TXN-000016` seam into a *characterized class* of (OWASP attack × FATF typology)
pairs. The paper-critical objection to defeat is *"isn't the seam circular?"* —
that the two detections secretly share the same signal. The anchor seam answered
this per-instance with a memo-blindness test; a *class* claim needs the answer to
be a uniform property of every pair, not a test re-written five times. M1-01 must
also re-express the existing P1 seam THROUGH the framework without weakening any
of its assertions (faithfulness), and must represent a *non-binding* pair (P4, the
honest boundary) in the same structure as a binding one.

**Decision.** Add `keystone.assurance.framework` on the edge (import-linter KEPT;
core stays attack-unaware). A `SeamPair` = `AttackSide` (OWASP id + canonical
`VulnerabilitySignature` + `AttackChannel`) × `CrimeSide` (FATF `Typology` +
detector) × `SeamResult` (CLEAN / BOUNDARY / OPEN). `bind(pair)` enforces the three
binding mechanisms once (single source of truth by signature identity;
demonstration-not-coincidence via a shared operative transaction id;
build-failing `SeamDriftError` on disagreement).

The independence guarantee is encoded **structurally, not by discipline**:
`bind` only ever hands the crime detector a `FinancialProjection` — the event with
the attack channel (the memo) stripped by `project_financial` — and `CrimeSide.detect`
is *typed* `Callable[[FinancialProjection], list[Finding]]`, so a detector cannot be
handed a raw, attack-bearing `Transaction` stream. The property is then asserted once
over `keystone.assurance.pairs.REGISTERED_PAIRS` rather than per pair. A BOUNDARY
pair's result IS the proven negative (`bind` asserts zero typologies fire). P1 is
re-expressed as `P1_PAIR` and binds through the framework with every existing seam
test unchanged.

**Alternatives rejected.** (a) *Keep memo-blindness as a per-pair test* — does not
scale to a class claim and leaves independence as a convention a refactor can break.
(b) *Project to a memo-free financial model and refactor `core.fatf` onto it* — would
change the core's meaning and risk P1's semantics for no added rigor, since the
detector is already memo-blind; the wrapper type achieves structural independence
without touching core. (c) *Let `bind` pass the raw stream "because the detector is
memo-blind anyway"* — rejected outright; that is exactly the circularity the property
must defeat.

**Consequences.** Pairs M1-02..M1-05 inherit independence + drift-protection by
construction; adding a pair is registering a `SeamPair`, and it is automatically
subjected to the framework-level property tests. The crime detector for every pair
must be expressible over the financial projection (true for the existing FATF
typologies). P5's recipient/sanctions typology does not yet exist in the engine
(`M1-00` §7a) — that is a build question for M1-05, not a framework limitation; the
framework already models its `TOOL_CALL` channel and `OPEN` result.

---

## ADR-0015 — Honestly multi-agent now: two genuine agents, gated by a strict bar

**Status:** Accepted · **Date:** 2026-07-03

**Context.** "Agentic" is the most abused word in this space. Keystone spent most
of its life as an *orchestrated, deterministic-by-design* workflow and said so —
it refused to call a `for`-loop an agent. Two honesty probes forced the question:
`agentic_audit.md` (is anything here really an agent?) and
`multi_agent_feasibility.md` (does a genuine second agent earn its place?).

**Decision.** Ship two agents only once each clears a **§2 agency bar**: the next
action must *demonstrably depend on what the agent observed*, over a genuine ≥2-option
space — proven by a build-failing test, not asserted in prose. The **Red-Team Agent**
(`keystone.agents.red_team`) observes each probe's outcome and adapts its next choice
over the 23-probe Garak prompt-injection space (`test_red_team_agent.py`: flip the
observations → the probe sequence flips). The **Triage Agent** (`keystone.agents.triage`)
routes a finding on the *interplay* of its signals — the SAME failure_rate routes
differently by seam context (`test_triage_agent.py`). The topology is supervisor
(Triage) over worker (Red-Team): reason → act → observe → adapt.

**Consequences.** The present-tense "multi-agent system" claim is defensible and
verifiable by reading the code. Every doc was moved from "*becoming*" to present
tense in this consolidation.

**Honest caveat.** They are agents by the §2 bar, **not** LLMs — they reason through
explicit, transparent policies. See ADR-0017.

## ADR-0016 — The memo-blind boundary is sacred: independence is the whole thesis

**Status:** Accepted · **Date:** 2026-07-03

**Context.** The convergence result (Movement 2) claims a seam event turns named
obligations from *violated* to *satisfied*. The paper-critical objection is
circularity: what if detection and reporting secretly share the same signal? If
they do, the convergence proves nothing.

**Decision.** Keep detection and reporting **structurally independent** and enforce
it mechanically, not by discipline. `bind` only ever hands the crime detector a
memo-stripped `FinancialProjection` (ADR-0014), and an **AST import-scan test**
proves the agent modules cannot even import the detector — `test_red_team_boundary.py`
and `test_triage_boundary.py` assert the boundary holds with **both** agents present.

**Consequences.** The convergence and seam-matrix claims rest on a property a refactor
cannot silently break; adding an agent does not erode independence.

**Honest caveat.** Independence is only as meaningful as the boundary test's reach; it
is an *import/data-flow* guarantee, not a proof of semantic non-leakage beyond the
projected fields — which is why the projection type (ADR-0014) is the real guardrail.

## ADR-0017 — Option B (policy) ships before Option A (LLM)

**Status:** Accepted · **Date:** 2026-07-03

**Context.** An agent can reason via an explicit policy (Option B) or via model
inference (Option A). It is tempting to claim "LLM agent" for the credibility while
shipping a policy.

**Decision.** Ship **Option B** — observation-driven policies (`choose_next`,
`route_for`) — and say so, everywhere, plainly: "an adaptive policy, NOT an LLM
agent." Option B still clears the §2 bar. Option A (LLM-reasoned selection/triage)
is a named later upgrade, not a silent gap.

**Consequences.** The demo stays deterministic and auditable (record/replay, schema
v7); the honesty framing is consistent across README, ARCHITECTURE, ROADMAP, and the
agent docstrings.

**Honest caveat.** Option A would add genuine natural-language reasoning and
generalization the policy cannot; until it lands, "reasoning" means *policy* reasoning.
Tracked in `OPEN_QUESTIONS.md` §B.

## ADR-0018 — Determinism-by-design is a feature, not a gap

**Status:** Accepted · **Date:** 2026-07-03

**Context.** In an "agentic" competition, deterministic stages can read as
un-ambitious. Keystone deliberately keeps FATF detection, the seam binding, and the
ledger deterministic.

**Decision.** Frame determinism as a **feature** wherever auditability demands it:
reproducibility, a tamper-evident hash-chained ledger, and record/replay demos.
Reasoning lives at the edge (the two agents, the LLM phrasing); the auditable core
stays deterministic on purpose.

**Consequences.** A regulator/mentor can re-run and get the same evidence; the
contrast between deterministic stages and reasoning agents is made visible in the
run-view (UI-03).

**Honest caveat.** Determinism-by-design is the right default *for the auditable
core* — it is not a claim that everything should be deterministic; the agentic edge
is exactly where non-determinism is allowed to earn its place.

## ADR-0019 — "remediate" is a route, not fix-selection (Movement C gate)

**Status:** Accepted · **Date:** 2026-07-03

**Context.** The Triage Agent routes findings to remediate / accept / escalate. It
would be an overclaim to present "remediate" as the system *choosing a fix*.

**Decision.** "remediate" is a **ROUTE** — *this finding warrants remediation* — not
a selection among concrete fixes. A defense agent that picks a fix (Movement C) is
**gated on a real ≥2-remediation menu**: a single rail is one choice, not an agent.

**Consequences.** The triage claim stays honest and testable (all three routes
reachable) without implying a capability that is not built.

**Honest caveat.** Until a genuine ≥2-remedy menu exists, there is no defense agent;
Movement C is deferred (`OPEN_QUESTIONS.md` §B).

## ADR-0020 — The deck leads problem-first, on the buyer-split

**Status:** Accepted · **Date:** 2026-07-03

**Context.** The technically interesting artifact is the seam; the *compelling* story
is the problem. The market gap is that no single vendor spans the seam — detection
vendors and reporting/compliance vendors are different buyers.

**Decision.** Lead the deck **problem-first** and on the **buyer-split**: the seam
exists because no vendor owns both sides, which is why the risk it addresses is
un-owned today. The seam thesis follows from the problem, not the reverse.

**Consequences.** The narrative lands for a non-technical judge; the technical depth
(seam framework, convergence, agents) is the *evidence*, not the pitch.

**Honest caveat.** The buyer-split is a positioning argument, not a repo-verifiable
fact; market claims (breadth, adoption) belong to the deck and are tracked as
unverifiable-from-repo in `OPEN_QUESTIONS.md` §A.

## ADR-0021 — The live Triage Agent: LLM reasoning is opt-in, fallback is the safety architecture, the record is honest by tag

**Status:** Accepted · **Date:** 2026-07-03

**Context.** ADR-0017 shipped the Triage Agent as Option B (a transparent policy) and
named Option A (LLM-reasoned) as a later upgrade. OPT-A-01 builds it: a local LLM
(qwen2.5:3b via Ollama) reasons the route. Three real risks a judge probes: (1)
non-determinism vs. our reproducibility guarantees, (2) the deferred 3B-on-4GB
reliability question, (3) the temptation to *claim* LLM reasoning while shipping a
fallback.

**Decision.** Live is **strictly additive and opt-in** (`--live`); the offline console
arc stays the default and stays deterministic (policy or recorded trace), and works
with **no Ollama**. The **fallback is the safety architecture, not a nicety**: an
unavailable / timed-out / unparseable / out-of-space LLM answer falls back to the
proven policy, so the route is *always* produced — live can never be worse than offline
at producing a valid route. The **record is honest by construction**: every decision
carries a `reasoner` tag (`policy` / `policy_fallback` / `llm:<model>`); a fallback is
never reported as an LLM decision. The LLM sees the **signals only** — never the memo /
attack channel (the memo-blind boundary, ADR-0016, stays sacred; the AST import-scan
still passes). No new LLM client (reuse `keystone.llm.inference.complete`, ADR-0008).
**No schema bump**: `TriageView.reasoner` defaults to `"policy"` — a run recorded before
live existed genuinely *was* a policy run, so old v7 data still loads and stays truthful.

**Consequences.** The first genuinely-live agent exists without weakening any guarantee:
offline-default intact, record/replay preserved, boundary intact, gates green. The
LLM-vs-policy question is answered *empirically*, not assumed (see the honest caveat).

**Honest caveat (the 3B finding).** In the OPT-A-01 evaluation (`make triage-eval`),
qwen2.5:3b **did not honor the signal interplay**: it collapsed toward `remediate` on
nearly every scenario and repeatedly **misread the numeric `failure_rate`** (calling
0.83 "no failure rate", 0.40 "very low"). Bounded selection held (it always returned a
valid route, never invented one), but selection *quality* was poor. Conclusion: the LLM
is genuine reasoning, but on this hardware it is **not yet trustworthy enough to be the
default** — which is exactly why the policy remains the default and the fallback. This
is the deferred 3B question answered, tracked in `OPEN_QUESTIONS.md` §B.

**Update (OPT-A-01b, ADR-0026).** This negative result was **revisited** with a genuine
prompt-engineering effort (the terse prompt above was a confound). With signal clarity +
few-shot + taught rules, in-distribution agreement rose **1/6 → 6/6** — but a **held-out
anti-parrot probe** stayed at **4/6** with the numeric misread resurfacing. Net: *part
prompt artifact, but the model ceiling is real*; the policy still stays the default. See
ADR-0026 for the honest before/after.

## ADR-0022 — The live Red-Team Agent: real Garak is opt-in, the recorded profile is the fallback, the source is honest by tag; LLM-selection is compute-gated

**Status:** Accepted · **Date:** 2026-07-03

**Context.** MA-01 shipped the Red-Team Agent as an adaptive policy that selects probes
but OBSERVES from the offline `RECORDED_DEFENSE_PROFILE` — the scan is characterized, not
live. OPT-A-02 makes the scanning genuinely live (real Garak). Two questions a judge
probes: (1) non-determinism/slowness vs. our offline-default guarantee, and (2) whether
we should also make probe *selection* LLM-reasoned.

**Decision.** Mirror ADR-0021's proven shape. Live Garak is **strictly additive and
opt-in** (the same `--live` flag drives both agents); the offline console arc stays the
default and works with **no Garak/Ollama**. `live_red_team` runs the **full
policy-selected sequence** as real Garak scans (`FULL_BUDGET` — the policy's own stop,
not a subset cap). The **recorded profile is the fallback, not a nicety**: on any Garak
failure (unavailable / target down / scan error → `GarakError`) it falls back to a
*complete* recorded run — the trace is always produced; only the observation *source*
degrades. The **record is honest by construction**: every `RedTeamTrace`/`RedTeamView`
carries a `source` tag (`garak_live` / `recorded_profile`); a fallback is never reported
as a live scan; `mechanism_for(source)` derives the matching human label. **No schema
bump**: `RedTeamView.source` defaults to `"recorded_profile"` — a run recorded before
live existed genuinely *was* a recorded-profile run, so old v7 data still loads and stays
truthful. Probe **SELECTION stays the adaptive policy** — no new Garak wrapper (reuse
`garak_observe`/`scan_mock_agent`, ADR-0003), and the memo-blind boundary (ADR-0016)
holds: live changes WHERE observations come from, never letting scan outcomes reach the
detector (the AST import-scan still passes).

**LLM-reasoned selection is explicitly compute-gated.** We deliberately do NOT add
LLM-reasoned probe selection. OPT-A-01 (ADR-0021) showed qwen2.5:3b can't reliably do
even a bounded 3-way choice over clean numeric inputs; probe selection over 23 options
with observed outcomes is a *harder* reasoning task, so LLM-selection would re-derive that
finding at greater cost. It is the documented, evidence-backed compute-gated frontier (the
NVIDIA ask), tracked in `OPEN_QUESTIONS.md` §B.

**Consequences.** The offensive worker's scanning becomes genuinely real — the
hardware-independent half of the live-agent frontier — without weakening any guarantee:
offline-default intact, record/replay preserved, boundary intact, gates green. The matrix
(Movement 1) stays characterized: live makes the *agent's scan* real, not the whole
matrix.

**Honest caveat (the operational reality).** A live scan is **slow and
environment-dependent** — it needs Garak 0.15.1, the vulnerable target, and Ollama
(qwen2.5:3b) running, and it re-fetches probe resources. One probe is ~30–60s at
`prompt_cap=12`; the full policy-selected sequence is on the order of minutes. That is
exactly why live is opt-in and record/replay exists — not a failure, the honest profile
of real scanning.

## ADR-0023 — The recorded defense profile is refreshed to real OPT-A-02 captures (fixing a characterization drift)

**Status:** Accepted · **Date:** 2026-07-04

**Context.** The Red-Team Agent's offline `RECORDED_DEFENSE_PROFILE` was a formula
characterization anchored to one real capture (the `latentinjection` lead). OPT-A-02's
real Garak scans surfaced a **drift**: the profile characterized the `promptinject`
family as fully **blocked**, but a real scan of its lead (`HijackHateHumans`) shows it
**gets through 11/12** on the qwen2.5:3b target. A characterization had gone stale versus
reality — exactly the kind of thing live scanning exists to catch.

**Decision.** Refresh `RECORDED_DEFENSE_PROFILE` to the **real observed outcomes** wherever
an OPT-A-02 live scan completed (`_OPT_A_02_CAPTURES`: 10 `latentinjection` probes + the
`promptinject` lead, garak 0.15.1 / qwen2.5:3b / prompt_cap=12). This is a **data refresh,
not a logic change** — the agent's policy, the arc, the schema, and the memo-blind boundary
are untouched; the agent now simply observes accurate recorded data. Probes whose live scan
did **not** complete (the deep `*Full` variants that timed out / were not reached, and the
`promptinject` probes past the lead) are left as **conservative characterizations** — real
values are used ONLY where a real scan captured them; **nothing is invented** (OPT-A-02 §4).

**Consequences.** The recorded profile is now anchored to *more real data* than before —
strengthening the "the recorded trace is a faithful replay of real scans" claim. The
demo's headline is preserved (the seam still binds; `latentinjection` is still exploited —
its lead ties `promptinject`'s and wins the tie-break; triage still ESCALATEs), with the
triage `failure_rate` now reading the accurate **0.92**. The one visible change: **both**
families now get through, so the agent **abandons nothing** in the recorded run (the old
"abandon the blocked family" beat is gone from the recorded demo). The abandon-a-blocked-
family behaviour remains covered by the synthetic §2 agency tests
(`tests/test_red_team_agent.py`). `recorded_run.json` regenerated; recorded==fresh holds;
the hash chain re-verifies.

**Honest caveat.** `latentinjection` and `promptinject` leads both scan ~11/12 on this
target — the tie-break (family order) is what keeps `latentinjection` the exploited family;
this is a stable ordering choice, not a claim that latent is "more" exploitable than
promptinject on qwen2.5:3b (they are comparable). The uncaptured deep probes remain
characterizations, flagged as such in the code.

## ADR-0024 — Data-residency, not "offline": the load-bearing requirement is no-exfiltration

**Status:** Accepted · **Date:** 2026-07-04

**Context.** The system had been justified as "offline-default", which reads as a
*limitation* ("works without internet"). The real requirement in regulated finance is
**data residency / no-exfiltration**: sensitive transaction data and PII must never leave
the institution's **trust boundary** to a third-party API. "Offline" was only ever a proxy
for that.

**Decision.** Correct the **framing** (not the behaviour) across the docs (README,
ARCHITECTURE, CLAUDE, `core-principles.md`, MEMORY). The principle is
**data-residency-preserving: all inference runs local / on-prem; no sensitive data crosses
the trust boundary.** The offline console arc is retained and reframed as the **proof** of
the no-exfiltration path — the *strongest* form, since it runs the whole flow with **zero
network**, a guarantee no cloud-API system can make. The compute ask (capable models for
LLM-reasoned decisions) is correspondingly an ask for **on-prem NVIDIA inference (NIM
inside the trust boundary)** — capable models *without data leaving* — never "more
internet".

**Consequences.** The zero-network property flips from an apparent limitation to the
headline security guarantee; the NVIDIA ask sharpens to "self-hosted capable inference",
which is both more credible and more valuable to a regulated buyer.

**Honest caveat.** This is a **framing sharpening, not a new capability**. On-prem NIM is a
**design target, not deployed**; the claim is that the architecture is *built for* on-prem
inference (inference is already local via Ollama) and the offline path *proves*
no-exfiltration. No existing honesty caveat is weakened.

## ADR-0025 — Two hardware experiments + a fine-tuning frontier define the evidence-backed on-prem compute ask

**Status:** Accepted · **Date:** 2026-07-04

**Context.** The live-agent builds (OPT-A-01, OPT-A-02) produced two concrete empirical
findings about what current local hardware can and cannot do. Captured together, they make
the compute ask **airtight** — a strength (rigour), not a gap.

**Decision.** Record the two findings as the joint evidence base, and name the flagship
compute-gated frontier they point to:

- **Finding 1 (OPT-A-01, ADR-0021) — small-model reasoning is unreliable for triage.**
  qwen2.5:3b agreed with the policy on **1 of 6** scenarios, **collapsed to a single route**
  on all 18 calls, **misread the numeric `failure_rate`**, and ignored the signal interplay.
  Bounded selection held (it always returned a *valid* route) but selection *quality* was
  poor. → the policy stays the default; the LLM path is opt-in. **Refined by OPT-A-01b
  (ADR-0026):** a genuine prompt effort lifts in-distribution agreement to 6/6, but a
  held-out probe stays at 4/6 (the numeric misread resurfaces) — part prompt, but the
  ceiling is real; the conclusion (policy stays default) is unchanged and better-evidenced.
- **Finding 2 (OPT-A-02, ADR-0022) — local Garak scanning is intractably slow.** Lead probes
  ran ~45–145s, deep probes **955–1550s+**, and one exceeded the 1800s per-scan timeout; the
  full sequence is **hours**. → the recorded profile stays the default; live is opt-in.
  *Positive corollary:* the live run **caught a real characterization drift** (promptinject
  blocked-in-profile but gets-through-live, ADR-0023) — live scanning earns its keep by
  catching drift.
- **The frontier (roadmap, NOT built) — a purpose-fine-tuned small model for the agents'
  decisions** (triage routing, probe selection): specialized enough to beat general models on
  our *narrow, bounded* tasks, and small enough to run **fully on-prem**, eliminating any
  external inference dependency. The training signal already exists — the policies' decisions
  across scenarios are labelled examples. This is the honest resolution of Findings 1 & 2 and
  the end-state of the data-residency + capability story (on-prem, specialized, no external
  API). A natural NVIDIA / NeMo / Nemotron fine-tuning mentorship project.

**Consequences.** "What we need from NVIDIA" becomes precise and evidence-backed: **capable
on-prem inference** (ADR-0024) — either a larger NIM-served model *inside the boundary* or a
fine-tuned small specialist — to make the agents' *decisions* LLM-reasoned without exfiltration.

**Honest caveat.** Fine-tuning is a **named future direction, not built**; no fine-tuned model
exists in the repo. The findings are what current hardware showed, not a claim that a bigger
model *would* clear the bar — that is the experiment the compute ask funds.

## ADR-0026 — The Triage LLM prompt-rescue: OPT-A-01's poor routing was PART prompt, but a held-out probe confirms the model ceiling

**Status:** Accepted · **Date:** 2026-07-04

**Context.** ADR-0021 / Finding 1 (ADR-0025) recorded a negative result: qwen2.5:3b agreed
with the triage policy on only **1/6** scenarios, collapsed to one route, and misread the
numeric `failure_rate`. But a poor result on a terse prompt is as consistent with a **weak
prompt** as with a weak model. Before "3B can't route" is treated as settled, we owed the
model a **genuine prompt-engineering effort** and a re-run of the **same** evaluation
(OPT-A-01b). Two outcomes were both valuable: it improves (partly a prompt artifact) or it
still fails after real effort (the ceiling is the model — a stronger compute ask).

**Decision.** Change the **prompt only** — the policy (`route_for`, ground truth + fallback),
the fallback, reasoner-tagging, the memo-blind boundary, the schema, and the opt-in default
are all untouched. The rewrite applies four levers targeting the specific OPT-A-01 failures:
(1) **signal clarity** — `failure_rate` presented with its 0.00–1.00 scale and an explicit
percent, so the number cannot be misread; (2) **the task taught in words** — the policy's
decision rules in order (HIGH→escalate; `<0.10`→accept; then seam open/boundary/clean); (3)
**five few-shot examples** — signal→route→why, all three routes + the interplay case + the
HIGH override, at **held-out rates** (0.65/0.05/0.90) that never equal an eval tuple and each
**verified against `route_for`** (a mechanical test pins this); (4) **structured output**.
SIGNALS ONLY — no memo/attack text (boundary sacred; AST import-scan still passes).

**Findings (the honest before/after, `make triage-eval`, not cherry-picked).**
- **In-distribution (the SAME 6 scenarios OPT-A-01 measured): 1/6 → 6/6**, stable (18/18 at
  3×, **30/30 at 5×**). No collapse; it reads the rate (0.02 → "below the 0.10 floor"); it
  honors interplay (0.50 → remediate/accept/escalate by seam). A dramatic, real improvement.
- **Held-out anti-parrot probe (6 novel (seam,severity)+rate combos the examples never show,
  each built so a parrot fails): 4/6 (12/18).** Two **stable** failures expose the ceiling:
  `0.25 clean LOW` → said **accept** (should remediate — it called a *clean* seam "provably
  contained", the *boundary* definition, parroting the wrong example); `0.06 open MED` → said
  **escalate** with rationale "failure_rate is above 0.10" — **0.06 is below 0.10**: the
  OPT-A-01 numeric misread, **resurfaced** on a held-out value. Even several *correct* routes
  carry **parroted rationales** (the arc case escalates for the right reason via HIGH but
  states "an open seam is unresolved" on a *clean* seam).

**Verdict — BOTH, which is the truthful reconciliation.** The OPT-A-01 finding was **partly a
prompt artifact**: signal clarity + few-shot lift in-distribution accuracy enormously (1/6→6/6).
**AND the model ceiling is real**: on held-out combos 3B falls to 4/6, still misreads the rate
and misapplies seam semantics. It **pattern-matches the worked examples; it does not robustly
apply the rules.** A headline 6/6 that hides a held-out 4/6 is *not* trustworthy — so the
**policy stays the default**, now with **stronger** evidence than a terse-prompt negative could
give. Promoting LLM routing to the default was **not** taken here — that remains a separate,
joint decision, and this result does not justify it.

**Consequences.** Refines Finding 1 (ADR-0025) without overturning it, and **hardens the
compute ask**: we now know *proper prompt engineering alone does not clear the bar* on 3B for
this bounded task — which is precisely what a purpose-fine-tuned small on-prem model is for.
The **held-out anti-parrot probe is now a permanent block in `make triage-eval`**, so an
in-distribution 6/6 can never again be mistaken for robust reasoning.

**Honest caveat.** The eval is small (6 in-distribution + 6 held-out, 3–5× each); the held-out
set is designed to be *discriminating*, not exhaustive. The bounded claim: on THIS routing
task, prompt engineering fixes the in-distribution misreads but 3B does not generalize the
override rules reliably. This is a statement about qwen2.5:3b with real prompt effort — not a
claim that a larger or fine-tuned model would fail (that is the experiment the ask funds).
