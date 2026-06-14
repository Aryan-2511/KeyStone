# TASKS.md

> Working task list. Keep it short; move shipped items out.

## In progress

- [ ] Phase 0 harness — bootstrap tooling so `make check` is green.

## Phase 0 checklist

- [x] src-layout (`src/keystone/` with `__init__.py`, `py.typed`)
- [x] `pyproject.toml` (3.12 pin, deps, dependency-groups, Ruff/mypy/pytest)
- [x] `Makefile` (setup/format/lint/typecheck/test/test-all/audit/check/…)
- [x] `.pre-commit-config.yaml` (ruff, hygiene, detect-secrets + baseline)
- [x] `.github/workflows/ci.yml` (mirrors `make check`, Python 3.12)
- [x] Six docs + `.gitignore` + `.secrets.baseline` + `README.md`
- [x] Smoke test
- [ ] Full verification suite green (final gate)

## Next (Phase 1 — do NOT start until Phase 0 verified)

- [ ] NAT YAML workflow skeleton
- [ ] Hash-chained SQLite evidence ledger
- [ ] Inference config switch (NIM / Ollama)
