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
- **Date comparisons in gates must be UTC-explicit**, not `date.today()` (local).
  KS-0205's `scripts/validate_obligations.py` compares `citation.retrieved`
  against `datetime.now(timezone.utc).date()`, today-inclusive — a local-clock
  `today()` made CI (UTC) and local diverge on the same correct data. (2026-06-17)
- **`retrieved` is advisory (ADR-0012), so a future-dated `retrieved` is a
  non-fatal WARNING, not a build error** in KS-0205's validator. Substantive
  checks (instrument match, provision pattern incl. RBI-by-name, required
  citation fields, duplicate id, https url) stay hard, build-failing errors.
  `validate()` returns hard errors; `check()` returns `(errors, warnings)`.

## Control library / crosswalk (KS-0202, `keystone.core.controls`)

- **Control id convention: `CTL-<DOMAIN>-<NN>`** (pattern `^CTL-[A-Z]+-\d{2}$`),
  e.g. `CTL-GOV-01`. Own data file (Option A, ADR-0012 §5): obligations reference
  controls by `control_id`; the crosswalk is a LOOKUP on `control_ids`, never a
  clustering of obligation text.
- **Control count is an OUTPUT, not a target.** Honest grouping of the 28
  obligations at natural granularity yielded **15 controls**; 1:1 mappings are
  legitimate (HUMAN/RIGHTS/CHILD/TPRM). Never force-merge unrelated obligations
  to shrink the count. (DPDPA-008 / PMLA-012 map to multiple controls because the
  underlying section genuinely is a portmanteau.)
- **The crosswalk MUST preserve `enforcement_modality`** through grouping: a
  control satisfied by both a HARD_LAW article and a SELF_CERTIFICATION sutra
  exposes BOTH modalities (`ControlMapping.modalities`). KS-0203 depends on this.
- **§5b referential integrity ships in `scripts/validate_controls.py`** (sibling
  of the citation gate): every `control_id` resolves, no orphan control, every
  obligation covered → hard errors; wired into `make verify` AND ci.yml.

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
