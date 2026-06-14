# Documentation index

The map of Keystone's knowledge base. `CLAUDE.md` (repo root) is the entry
point; this file indexes everything reachable below it. Every doc should be
reachable from here — orphans are flagged by the doc-freshness check.

## Governance (repo root)

| Doc | Purpose |
| --- | --- |
| [`../CLAUDE.md`](../CLAUDE.md) | Entry map: pointers, non-negotiables, commands |
| [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | Layers, dependency direction, components |
| [`../DECISIONS.md`](../DECISIONS.md) | ADR log (every structural choice) |
| [`../ROADMAP.md`](../ROADMAP.md) | Human-readable phase plan |
| [`../TASKS.md`](../TASKS.md) | Human-readable working task view |
| [`../MEMORY.md`](../MEMORY.md) | Durable project facts (not live state) |

## Design

| Doc | Purpose |
| --- | --- |
| [design/core-principles.md](./design/core-principles.md) | Domain + golden principles; non-negotiables |
| [design/architecture-boundaries.md](./design/architecture-boundaries.md) | The enforced dependency contract (import-linter) |
| [design/observability.md](./design/observability.md) | Observability — explicitly deferred (documented slot) |

## Execution & quality

| Path | Purpose |
| --- | --- |
| [exec-plans/](./exec-plans/) | Live session state: `active/` and `completed/` plans |
| [QUALITY.md](./QUALITY.md) | Grading/acceptance criteria (the evaluator's rubric) |
| [feature_list.json](./feature_list.json) | Machine-checkable features + done-criteria (source of truth) |

## Reference & generated

| Path | Purpose |
| --- | --- |
| [references/](./references/) | External library dumps (`*-llms.txt`), pinned reading |
| [generated/](./generated/) | Derived docs — never hand-edited |

## The three-way state split

Keystone keeps three distinct stores; do not conflate them:

1. **`MEMORY.md`** — durable, versioned facts true across all sessions.
2. **`docs/exec-plans/`** — live, per-task state (progress, decisions, next
   steps) that survives context resets.
3. **Agent memory store** — the runtime/ephemeral memory of a given agent run;
   not the system of record. Promote anything durable into 1 or 2.
