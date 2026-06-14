<!--
Exec-plan template. Copy to docs/exec-plans/active/<task-slug>.md when starting a
task (the /new-exec-plan command does this). Keep it current AS YOU WORK — it is
the handoff that lets any future session resume cleanly. On completion, run the
verify gate and move the file to docs/exec-plans/completed/ (the /finish-task
command does this). See ../README.md and ../../index.md (three-way state split).
-->

# Exec-plan: <task title>

- **Slug:** `<task-slug>`
- **Feature IDs:** <e.g. KS-0102, KS-0103 — from docs/feature_list.json, or "none">
- **Status:** active <!-- active | blocked | done -->
- **Started:** <YYYY-MM-DD>
- **Owner (session):** <agent/human>

## Goal & acceptance

What "done" means for this task. Link the relevant `done_criteria` from
`feature_list.json` and the applicable rows of `docs/QUALITY.md`.

## Context / constraints

Pointers an incoming session needs (files to read, ADRs that bind this work,
non-negotiables that apply). Keep it terse — link, don't paste.

## Plan

- [ ] Step 1
- [ ] Step 2
- [ ] Verify: `make verify` green
- [ ] Update `feature_list.json` (status + tests) and human views

## Progress log

Append-only, newest at the bottom. One dated line per meaningful step.

- <YYYY-MM-DD> created plan.

## Decisions

Structural choices made while working. Each one also gets an ADR in
`DECISIONS.md`; link it here (e.g. "see ADR-00NN").

## Open questions / blockers

Anything needing a human decision. Don't silently fill these.

## Next steps (resume here)

The single most useful section for a cold start: exactly what to do next.

## Handoff (fill in on completion)

- What changed, what was verified (paste the gate result).
- What was deferred and why.
- Recommended next task.
