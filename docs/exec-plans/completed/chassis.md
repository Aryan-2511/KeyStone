# Exec-plan: Phase 1 chassis (skeleton mesh)

- **Slug:** `chassis`
- **Feature IDs:** KS-0101 (NAT skeleton), KS-0102/KS-0103 (ledger), KS-0104 (inference switch)
- **Status:** done
- **Started:** 2026-06-15
- **Owner (session):** agent

## Goal & acceptance

Build the empty mesh all three layers bolt onto — no compliance logic, no real
agents. Done when `make check`, `make phase-check`, and `make demo` are green and
the milestone test proves exactly 3 layer entries + a verifying chain.
Grade against `docs/QUALITY.md` (esp. the adversarial tamper test for the ledger).

## Context / constraints

- Layout decision (user): nest under layer packages — ledger=`keystone.core.ledger`,
  inference=`keystone.llm.inference`, orchestrator=`keystone.agents.orchestrator`,
  app=`keystone.ui.app`, run=`keystone.agents.run`. import-linter already guards
  `keystone.core` (ledger is deterministic, must not import the edge).
- Deterministic core / LLM edge: only `keystone.llm.inference` calls an LLM.
- Synthetic data only; config via env vars; no secrets logged.

## NAT API (verified against installed nvidia-nat 1.7.0)

- Register: `@register_function(config_type=Cfg)` on `async def build(cfg, builder)`
  that `yield`s `FunctionInfo.from_fn(callable, description=...)`.
- Config type name: `class Cfg(FunctionBaseConfig, name="keystone_x")` → YAML `_type`.
- Run: `async with load_workflow(yaml) as session: async with session.run(msg) as runner: await runner.result(to_type=str)`.
- `nat` is a namespace package. Registered functions must be imported before load.

## Plan

- [ ] Ledger: models + Ledger(append/all/verify_chain) + unit tests (good + mutated)
- [ ] Inference: Backend protocol + nim + ollama + env switch; fast tests w/ fake
- [ ] Orchestrator: layer_stub + orchestrator functions + workflow.yml + run.py
- [ ] Milestone test: run workflow, assert 3 layer entries + chain verifies
- [ ] Streamlit shell (keystone.ui.app): run button, ledger table, chain indicator
- [ ] Wire `make demo` to streamlit; extend import-linter contract notes
- [ ] Verify gate green; update feature_list, TASKS.md, MEMORY.md

## Progress log

- 2026-06-15 created plan; verified NAT API surface (no STOP).
- 2026-06-15 ledger (core) + adversarial tamper tests green.
- 2026-06-15 inference switch (nim/ollama) + fake-backend fast tests.
- 2026-06-15 NAT orchestrator + workflow.yml + run entrypoint; milestone green.
- 2026-06-15 Streamlit shell; `make demo` boots (HTTP 200).
- 2026-06-15 docs/feature_list/TASKS/MEMORY/ADR-0010 updated; all gates green.

## Decisions

- Module layout nested under layer packages (per user choice) — ADR-0010.
- NAT untyped boundary: scoped mypy relaxation for `agents.orchestrator.*` only
  (no inline ignores) — ADR-0010.

## Open questions / blockers

- None.

## Next steps (resume here)

Phase 2 (KS-0201/0202): real compliance/assurance agents on the workflow +
NeMo Guardrails rails. The mesh, ledger, and inference switch are ready to use.

## Handoff

- **Changed:** added `keystone.core.ledger`, `keystone.llm.inference`,
  `keystone.agents.orchestrator` (+ `run`), `keystone.ui.app`; tests for each;
  `make demo` wired to Streamlit; feature list KS-0101/0102/0103/0104 → done.
- **Verified:** `make check` exit 0 (30 tests, cov 82%); `make phase-check` (1
  milestone: 3 layer entries + chain verifies); `python -m keystone.agents.run`
  prints 3 entries chain_ok; `make demo` serves HTTP 200.
- **Deferred:** real agents/policy/guardrails (Phase 2); Garak (Phase 3); live
  inference exercised only by the `slow` test (skips if no backend).
- **Recommended next task:** Phase 2 — KS-0201 compliance agent.
