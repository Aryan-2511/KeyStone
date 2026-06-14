# QUALITY.md — acceptance criteria & grading rubric

The **evaluator's** checklist. A change is "done" only when every applicable
criterion below holds. This is deliberately separate from the work itself
(generator/evaluator separation): run [`make verify`](../Makefile) as the
skeptical, independent gate — it must fail loudly rather than rationalize gaps.

> **Coverage is a floor, not a grade.** A high coverage % does not mean a change
> is correct. Line coverage proves code *ran*, not that it was *asserted*. Grade
> on the strength of assertions and the presence of behavioral + adversarial
> tests — not on the percentage. The `--cov-fail-under` floor only blocks
> regressions; clearing it is necessary, never sufficient.

## Acceptance criteria

| # | Criterion | How it's checked |
| - | --- | --- |
| 1 | **All tests pass** (full suite, incl. `slow`/`milestone`) | `make verify` → `pytest` |
| 2 | **Real behavior asserted** — surfaces have an end-to-end test that exercises the actual entry point, not just an import | e2e tests in `tests/e2e/` |
| 3 | **Scope is valid** — `feature_list.json` validates; the worked item's `done_criteria` are met and its `tests` exist and pass | `scripts/validate_feature_list.py` |
| 4 | **Types** — mypy strict clean; no new `# type: ignore` | `make typecheck` |
| 5 | **Lint/security** — ruff clean incl. `S` (bandit) rules; no new `noqa` | `make lint` |
| 6 | **Architecture** — no forbidden imports (core must not import the edge) | `lint-imports` (Phase 4) |
| 7 | **Docs fresh** — `CLAUDE.md` thin, no broken links, structural decision has an ADR, exec-plan updated | `tests/test_docs.py`, review |
| 8 | **Synthetic data only** — no real data; no secrets | `detect-secrets`, review |
| 9 | **Coverage floor held** (regression guard only — see banner above) | `--cov-fail-under` |

## Grading guidance for critical code

Some code earns scrutiny beyond the table:

- **Evidence ledger (hash chaining):** require an *adversarial* test — mutate /
  insert / delete an entry and assert verification fails. "It appends" is not
  enough.
- **Inference config switch:** assert the same code path is taken for both
  backends and that an invalid backend is rejected with a clear error.
- **Guardrails:** assert a disallowed input/output is actually blocked, not just
  that the rail is wired.

## What "done" is NOT

- Coverage went up. (See banner.)
- The happy path works. (Grade the failure paths.)
- "It probably works" without an e2e assertion on the real surface.
- A gate was relaxed / a rule `noqa`'d to go green. (Forbidden — fix or ask.)
