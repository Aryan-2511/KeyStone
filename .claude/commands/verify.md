---
description: Run the skeptical acceptance gate (make verify)
---

Run the independent verification gate and report honestly.

1. Run `make verify` (lint + typecheck + arch + scope validation + FULL test
   suite incl. slow/milestone/e2e + coverage floor + audit).
2. If it fails: report the failure verbatim. Do **not** weaken a gate, relax a
   rule, lower the coverage floor, or add a `# type: ignore` / broad `noqa` to
   go green — fix the underlying issue or surface it for a decision.
3. If it passes: confirm green and paste the salient output (test count,
   coverage, contracts kept).

Grade against `docs/QUALITY.md`, not just exit code: remember **coverage is a
floor, not a grade** — check that real behavior is asserted (e2e on the actual
surface) and that critical code has adversarial tests.
