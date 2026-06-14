# Exec-plans

Live, per-task working state — the structured handoff that survives context
resets. This is **state**, distinct from `MEMORY.md` (durable facts) and the
runtime agent memory store. See the three-way split in [../index.md](../index.md).

## Layout

- `active/` — plans for in-flight tasks. One file per task:
  `active/<short-task-slug>.md`.
- `completed/` — plans moved here on finish, as a durable record.

## Lifecycle

1. Start a task → copy [`TEMPLATE.md`](./TEMPLATE.md) to `active/<slug>.md`
   (the [`/new-exec-plan`](../../.claude/commands/new-exec-plan.md) command does
   this).
2. Work → keep the plan's progress log and decision log current as you go.
3. Finish → run the verify gate, then move the plan to `completed/` with a final
   handoff (the [`/finish-task`](../../.claude/commands/finish-task.md) command
   does this).

The [`/verify`](../../.claude/commands/verify.md) command runs the acceptance
gate at any time.
