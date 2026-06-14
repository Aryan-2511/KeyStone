---
description: Finish a task — verify, update scope, write handoff, archive the plan
argument-hint: [task-slug]
---

Close out a task cleanly so the repo is left in a verifiable, resumable state.
Work the checklist in order; stop and report if any step can't pass.

1. **Verify.** Run `make verify`. It must exit 0. Never relax a gate to get
   there — fix the code or surface the blocker.
2. **Update scope.** In `docs/feature_list.json`, set the worked item(s) to the
   right status and ensure `tests` references real, passing tests (the validator
   enforces this once status passes `planned`). Update `TASKS.md`/`ROADMAP.md`
   (human views) to match.
3. **Record decisions.** Every structural choice from this task has an ADR in
   `DECISIONS.md` (and a row in the ADR index table). Link them from the
   exec-plan's **Decisions** section.
4. **Docs fresh.** `CLAUDE.md` still thin, no broken links, any new doc reachable
   from `docs/index.md`. (`tests/test_docs.py` checks this.)
5. **Write the handoff.** Fill the exec-plan's **Handoff** section: what changed,
   what was verified (paste the gate result), what was deferred and why, and the
   recommended next task.
6. **Archive.** Move `docs/exec-plans/active/<task-slug>.md` to
   `docs/exec-plans/completed/`.
7. **Commit** with a clear message (and the `Co-Authored-By` trailer). Commit or
   push only if the user has asked.

Cleanup checklist (entropy control): no leftover TODO/`xfail`/skips without a
written reason; no commented-out code; no synthetic-data/secret leakage; the
golden principles in `docs/design/core-principles.md` still hold.
