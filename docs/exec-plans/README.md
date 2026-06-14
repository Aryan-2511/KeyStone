# Exec-plans

Live, per-task working state — the structured handoff that survives context
resets. This is **state**, distinct from `MEMORY.md` (durable facts) and the
runtime agent memory store. See the three-way split in [../index.md](../index.md).

## Layout

- `active/` — plans for in-flight tasks. One file per task:
  `active/<short-task-slug>.md`.
- `completed/` — plans moved here on finish, as a durable record.

## Lifecycle

1. Start a task → create `active/<slug>.md` from the template (see the
   `new-exec-plan` command, added in the continuity phase).
2. Work → keep the plan's progress log and decision log current as you go.
3. Finish → run the verify gate, then move the plan to `completed/` with a final
   handoff (see the `finish-task` command).

_The template and the `.claude/commands/` helpers are added in the continuity
phase; the directories exist now so the structure is stable._
