# MEMORY.md — durable project facts

> Facts that are NOT derivable from the code or git history. One line each.
>
> **Role (one of three state stores — see [`docs/index.md`](docs/index.md)):**
> this file holds **durable facts true across all sessions**. Live, per-task
> state goes in [`docs/exec-plans/`](docs/exec-plans/); ephemeral runtime memory
> stays in the agent memory store. Don't duplicate exec-plan state here — only
> promote something to MEMORY.md when it's durable and cross-session.

- Python is pinned to **3.12 only** — verified intersection of nvidia-nat,
  nemoguardrails, and garak. Re-validate before bumping. (ADR-0001)
- **garak is intentionally absent from `pyproject.toml`** — it lives as an
  isolated `uv tool` and is called as a subprocess. Don't "fix" its missing-dep
  by adding it. (ADR-0003)
- The `keystone` console script and `make demo` are **Phase 0 placeholders** —
  no real CLI/demo wiring exists yet.
- Resolution fact (2026-06-14): `nvidia-nat` + `nemoguardrails` resolve together
  cleanly under 3.12 with `uv`; no hand-edited pins were needed.
- `annoy` (a Guardrails dependency) builds a native extension — a C/C++ compiler
  is a hard install prerequisite.

## NAT (nvidia-nat 1.7.0) integration notes — things that surprised us

- **`nat` ships no `py.typed`** (untyped). Under mypy strict this breaks
  `disallow_subclassing_any` (subclassing `FunctionBaseConfig`) and
  `disallow_untyped_decorators` (`@register_function`). We relax ONLY those two
  flags for ONLY `keystone.agents.orchestrator.*`, plus a `call-arg` waiver on
  `…orchestrator.config` for the `name=` class kwarg. Rest stays strict. (ADR-0010)
- **`nat` is a namespace package** (`nat.__file__` is None).
- **Register pattern:** `@register_function(config_type=Cfg)` on an
  `async def build(cfg, builder)` that `yield`s `FunctionInfo.from_fn(fn, ...)`.
  The config's `_type` in YAML = the `name=` passed to `class Cfg(FunctionBaseConfig, name=...)`.
- **`builder.get_function(name)` is async** (it's a `ChildBuilder` coroutine) —
  must `await` it; then `await fn.ainvoke(value, to_type=str)`.
- **Run pattern:** `async with load_workflow(yaml) as session, session.run(msg) as runner: await runner.result(to_type=str)`.
- **FunctionInfo.from_fn rejects param names with leading underscores** (pydantic
  builds the input schema from the signature) — use `message`, not `_message`.
- **load_workflow auto-discovers plugins** and noisily logs an import failure for
  `nat.tool.nvidia_rag` (needs `langchain_core`, not installed). Non-fatal — our
  functions register via direct import, and the workflow runs fine.
