---
description: Start a new exec-plan for a task (continuity handoff)
argument-hint: <task-slug> [feature IDs]
---

Create a new exec-plan so this task's state survives context resets.

Steps:

1. Pick a short kebab-case `<task-slug>` from `$ARGUMENTS` (or infer one from the
   task). Confirm it doesn't already exist under `docs/exec-plans/active/`.
2. Copy `docs/exec-plans/TEMPLATE.md` to `docs/exec-plans/active/<task-slug>.md`.
3. Fill in the header (slug, **Feature IDs** from `docs/feature_list.json`,
   started date = today), the **Goal & acceptance** (link the relevant
   `done_criteria` and `docs/QUALITY.md` rows), and the initial **Plan**.
4. Read `CLAUDE.md` and the pointers relevant to this task; record the key
   context links in **Context / constraints**.
5. Do NOT invent scope. If the task isn't represented in `feature_list.json`,
   note it under **Open questions** rather than adding features unilaterally.

Keep the plan's **Progress log** and **Decisions** current as you work. When the
task is done, run `/finish-task`.
